import io
import sys
import os

# 强制输出使用 UTF-8，防止在 Windows 上打印 emoji 报错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, request, jsonify, send_from_directory, Response, g
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)

    # 配置CORS，允许所有来源访问（支持内网穿透）
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # 允许所有来源（支持内网穿透域名）
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        },
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
            "expose_headers": ["Access-Control-Allow-Origin"]
        }
    })

    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/aigc_assistant?charset=utf8mb4')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'adminroot'

    # 文件上传配置
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('generated_images', exist_ok=True)

    # 初始化数据库
    from models.database import db
    db.init_app(app)

    # 导入模型
    from models.database import GenerationTask, GeneratedImage, GenerationContext, UserFeedback, ApiUsage, \
        GenerationHistory, User, InviteCode

    # 导入认证工具和服务
    from utils.auth import token_required, admin_required
    from services.user_service import UserService
    from services.invite_service import InviteService

    # 创建数据库表
    with app.app_context():
        db.create_all()
        logger.info("数据库表初始化完成")

    # 添加全局请求日志中间件
    @app.before_request
    def log_request_info():
        """记录所有进入的请求"""
        logger.info(f"📥 收到请求: {request.method} {request.path}")
        logger.info(f"   来源: {request.remote_addr}")
        logger.info(f"   Headers: {dict(request.headers)}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            logger.info(f"   Content-Type: {request.content_type}")

    @app.after_request
    def log_response_info(response):
        """记录所有响应"""
        logger.info(f"📤 响应: {request.method} {request.path} -> {response.status_code}")
        return response

    # 延迟导入服务（避免循环导入）
    def get_services():
        """获取服务实例"""
        from services.image_generator_manager import ImageGeneratorManager
        from services.prompt_builder import PromptBuilderService
        from services.context_manager import ContextManagerService
        from utils.image_processor import ImageProcessor
        from utils.oss_uploader import OSSUploader
        from config import Config

        # 初始化OSS上传器（如果启用）
        oss_uploader = None
        if Config.OSS_ENABLED:
            try:
                oss_uploader = OSSUploader(
                    access_id=Config.OSS_ACCESS_ID,
                    access_key=Config.OSS_ACCESS_KEY,
                    endpoint=Config.OSS_ENDPOINT,
                    bucket_name=Config.OSS_BUCKET
                )
                logger.info("OSS上传器初始化成功")
            except Exception as e:
                logger.error(f"OSS上传器初始化失败: {str(e)}")

        return {
            'image_generator_manager': ImageGeneratorManager(),
            'prompt_builder': PromptBuilderService(),
            'context_manager': ContextManagerService(),
            'image_processor': ImageProcessor(),
            'oss_uploader': oss_uploader
        }

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

    # ============ 用户认证API ============

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.json

            # 验证必需字段
            required_fields = ['phone', 'email', 'username', 'password', 'inviteCode']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'缺少必需字段: {field}'}), 400

            success, message, user_data = UserService.register_user(
                phone=data['phone'],
                email=data['email'],
                username=data['username'],
                password=data['password'],
                invite_code=data['inviteCode']
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user_data
                })
            else:
                return jsonify({'error': message}), 400

        except Exception as e:
            logger.error(f"注册错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.json

            # 验证必需字段
            if 'username' not in data or 'password' not in data:
                return jsonify({'error': '缺少用户名或密码'}), 400

            success, message, token, user_data = UserService.login_user(
                username_or_email=data['username'],
                password=data['password']
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'token': token,
                    'user': user_data
                })
            else:
                return jsonify({'error': message}), 401

        except Exception as e:
            logger.error(f"登录错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def get_current_user():
        """获取当前登录用户信息"""
        try:
            user_data = UserService.get_user_info(request.user_id)
            if user_data:
                return jsonify({
                    'success': True,
                    'user': user_data
                })
            else:
                return jsonify({'error': '用户不存在'}), 404

        except Exception as e:
            logger.error(f"获取用户信息错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/change-password', methods=['POST'])
    @token_required
    def change_password():
        """修改密码"""
        try:
            data = request.json

            # 验证必需字段
            if 'oldPassword' not in data or 'newPassword' not in data:
                return jsonify({'error': '缺少旧密码或新密码'}), 400

            success, message = UserService.change_password(
                user_id=request.user_id,
                old_password=data['oldPassword'],
                new_password=data['newPassword']
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({'error': message}), 400

        except Exception as e:
            logger.error(f"修改密码错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # ============ 管理员API ============

    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_users():
        """获取所有用户列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            success, message, users, pagination = UserService.get_all_users(
                admin_id=request.user_id,
                page=page,
                per_page=per_page
            )

            if success:
                return jsonify({
                    'success': True,
                    'users': users,
                    'pagination': pagination
                })
            else:
                return jsonify({'error': message}), 403

        except Exception as e:
            logger.error(f"获取用户列表错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/users/<int:user_id>/stats', methods=['GET'])
    @admin_required
    def get_user_stats(user_id):
        """获取用户统计信息"""
        try:
            success, message, stats = UserService.get_user_stats(
                admin_id=request.user_id,
                target_user_id=user_id
            )

            if success:
                return jsonify({
                    'success': True,
                    'stats': stats
                })
            else:
                return jsonify({'error': message}), 404

        except Exception as e:
            logger.error(f"获取用户统计错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @admin_required
    def delete_user(user_id):
        """删除用户"""
        try:
            success, message = UserService.delete_user(
                admin_id=request.user_id,
                target_user_id=user_id
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({'error': message}), 400

        except Exception as e:
            logger.error(f"删除用户错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
    @admin_required
    def reset_user_password(user_id):
        """管理员重置用户密码"""
        try:
            data = request.json

            # 支持两种参数名
            new_password = data.get('newPassword') or data.get('new_password')
            if not new_password:
                return jsonify({'error': '缺少新密码'}), 400

            success, message = UserService.reset_password_by_admin(
                admin_id=request.user_id,
                target_user_id=user_id,
                new_password=new_password
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({'error': message}), 400

        except Exception as e:
            logger.error(f"重置密码错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/invite-codes/generate', methods=['POST'])
    @admin_required
    def generate_invite_codes():
        """生成邀请码"""
        try:
            data = request.json
            count = data.get('count', 1)

            success, message, codes = InviteService.generate_invite_codes(
                admin_id=request.user_id,
                count=count
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'count': len(codes) if codes else 0,
                    'codes': codes
                })
            else:
                return jsonify({'error': message}), 400

        except Exception as e:
            logger.error(f"生成邀请码错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/invite-codes', methods=['GET'])
    @admin_required
    def get_invite_codes():
        """获取邀请码列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            status = request.args.get('status', None)

            success, message, codes, pagination = InviteService.get_invite_codes(
                admin_id=request.user_id,
                status=status,
                page=page,
                per_page=per_page
            )

            if success:
                return jsonify({
                    'success': True,
                    'invite_codes': codes,
                    'pagination': pagination
                })
            else:
                return jsonify({'error': message}), 403

        except Exception as e:
            logger.error(f"获取邀请码列表错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/invite-codes/stats', methods=['GET'])
    @admin_required
    def get_invite_code_stats():
        """获取邀请码统计信息"""
        try:
            success, message, stats = InviteService.get_invite_code_stats(
                admin_id=request.user_id
            )

            if success:
                return jsonify({
                    'success': True,
                    'stats': stats
                })
            else:
                return jsonify({'error': message}), 403

        except Exception as e:
            logger.error(f"获取邀请码统计错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/invite-codes/<int:code_id>', methods=['DELETE'])
    @admin_required
    def delete_invite_code(code_id):
        """删除邀请码"""
        try:
            from models.database import InviteCode

            # 查找邀请码
            invite_code = InviteCode.query.get(code_id)
            if not invite_code:
                return jsonify({'error': '邀请码不存在'}), 404

            # 检查是否已使用
            if invite_code.status == 'used':
                return jsonify({'error': '已使用的邀请码不能删除'}), 400

            # 删除邀请码
            db.session.delete(invite_code)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '邀请码删除成功'
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"删除邀请码错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # ============ 金币系统API ============

    @app.route('/api/admin/coin-settings', methods=['GET'])
    @admin_required
    def get_coin_settings():
        """获取金币系统设置"""
        try:
            from services.coin_service import CoinService
            settings = CoinService.get_coin_settings()
            return jsonify(settings)
        except Exception as e:
            logger.error(f"获取金币设置错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/coin-settings', methods=['POST'])
    @admin_required
    def update_coin_settings():
        """更新金币系统设置"""
        try:
            from services.coin_service import CoinService
            data = request.json

            success, message = CoinService.update_coin_settings(
                mode=data.get('mode'),
                init_amount=data.get('init_amount'),
                daily_amount=data.get('daily_amount'),
                per_image=data.get('per_image')
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({'error': message}), 400
        except Exception as e:
            logger.error(f"更新金币设置错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/users/<int:user_id>/coins', methods=['POST'])
    @admin_required
    def recharge_user_coins(user_id):
        """给用户充值金币"""
        try:
            from services.coin_service import CoinService
            data = request.json
            amount = data.get('amount')

            if not amount or amount <= 0:
                return jsonify({'error': '充值金额必须大于0'}), 400

            success, message = CoinService.add_coins(
                user_id=user_id,
                amount=amount,
                operated_by=request.user_id
            )

            if success:
                # 返回更新后的用户信息
                user = User.query.get(user_id)
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user.to_dict() if user else None
                })
            else:
                return jsonify({'error': message}), 400
        except Exception as e:
            logger.error(f"充值金币错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/users/coins/batch', methods=['POST'])
    @admin_required
    def batch_recharge_coins():
        """批量充值金币"""
        try:
            from services.coin_service import CoinService
            data = request.json
            user_ids = data.get('user_ids', [])
            amount = data.get('amount')

            if not user_ids:
                return jsonify({'error': '请选择用户'}), 400
            if not amount or amount <= 0:
                return jsonify({'error': '充值金额必须大于0'}), 400

            success, message, failed_users = CoinService.batch_recharge_coins(
                user_ids=user_ids,
                amount=amount,
                operated_by=request.user_id
            )

            return jsonify({
                'success': True,
                'message': message,
                'failed_users': failed_users
            })
        except Exception as e:
            logger.error(f"批量充值错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/coins', methods=['GET'])
    @token_required
    def get_user_coins():
        """获取当前用户金币余额"""
        try:
            from services.coin_service import CoinService
            coins = CoinService.get_user_coins(request.user_id)
            user = User.query.get(request.user_id)

            return jsonify({
                'coins': coins,
                'user': user.to_dict() if user else None
            })
        except Exception as e:
            logger.error(f"获取用户金币错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/coin-transactions', methods=['GET'])
    @token_required
    def get_coin_transactions():
        """获取当前用户的金币交易记录"""
        try:
            from services.coin_service import CoinService
            limit = request.args.get('limit', 50, type=int)
            transactions = CoinService.get_transaction_history(request.user_id, limit)

            return jsonify({
                'transactions': transactions
            })
        except Exception as e:
            logger.error(f"获取交易记录错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-images', methods=['POST'])
    def generate_images():
        """
        生成图片的主要接口
        处理多图片输入和多类型输出的逻辑
        """
        try:
            data = request.json

            # 验证必需字段
            required_fields = ['productForm', 'selectedImageTypes', 'mainPrompt']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'缺少必需字段: {field}'}), 400

            # 创建生成任务
            task = GenerationTask(
                task_id=str(uuid.uuid4()),
                user_id=request.user_id,  # 关联用户
                user_input=json.dumps(data),
                status='pending',
                created_at=datetime.utcnow()
            )
            db.session.add(task)
            db.session.commit()

            # 异步处理图片生成
            executor = ThreadPoolExecutor(max_workers=3)
            future = executor.submit(process_generation_task, task.task_id, data)

            return jsonify({
                'success': True,
                'task_id': task.task_id,
                'message': '图片生成任务已启动',
                'estimated_time': len(data['selectedImageTypes']) * 30  # 估算时间（秒）
            })

        except Exception as e:
            logger.error(f"生成图片接口错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-images-stream', methods=['POST'])
    @token_required
    def generate_images_stream():
        """流式图片生成接口 - 并行版本"""
        from flask import Response
        import json
        import queue
        import threading
        import time

        try:
            data = request.json

            # 检查金币余额
            from services.coin_service import CoinService
            settings = CoinService.get_coin_settings()
            required_images = len(data.get('selectedImageTypes', []))
            required_coins = required_images * settings['per_image']

            user_coins = CoinService.get_user_coins(request.user_id)
            if user_coins < required_coins:
                return jsonify({
                    'error': f'金币不足！需要 {required_coins} 金币，当前余额 {user_coins} 金币',
                    'required_coins': required_coins,
                    'current_coins': user_coins,
                    'coins_insufficient': True
                }), 400

            # 创建或复用任务记录
            # 如果前端传了task_id，说明是在同一任务下继续生成，复用该task_id
            task_id = data.get('taskId') or str(uuid.uuid4())

            # 查找是否已存在该任务
            existing_task = GenerationTask.query.filter_by(task_id=task_id).first()

            if existing_task:
                # 更新现有任务
                logger.info(f"🔄 复用现有任务: {task_id}")
                existing_task.status = 'processing'
                existing_task.total_images += len(data.get('selectedImageTypes', []))
                existing_task.user_input = json.dumps(data)  # 更新输入参数
                db.session.commit()
            else:
                # 创建新任务
                logger.info(f"🆕 创建新任务: {task_id}")
                task = GenerationTask(
                    task_id=task_id,
                    user_id=request.user_id,  # 关联用户
                    user_input=json.dumps(data),
                    status='processing',
                    total_images=len(data.get('selectedImageTypes', [])),
                    created_at=datetime.utcnow()
                )
                db.session.add(task)
                db.session.commit()

            def generate_single_image(image_type, index, result_queue, services, data, task_id):
                """单个图片生成函数，用于并行执行"""
                try:
                    with app.app_context():  # 确保在应用上下文中执行
                        print(f"\n🎨 开始并行生成图片 {index + 1}: {image_type}")
                        logger.info(f"开始并行生成图片 {index + 1}: {image_type}")

                        # 构建提示词
                        type_specific_references = data.get('referenceImagesByType', {}).get(image_type, [])
                        prompt = services['prompt_builder'].build_prompt(
                            product_form=data['productForm'],
                            image_type=image_type,
                            main_prompt=data['mainPrompt'],
                            reference_images=[],
                            competitors=data.get('competitors', []),
                            type_specific_references=type_specific_references,
                            size=data.get('selectedSize', '1024x1024'),
                            ratio=data.get('selectedRatio', '1:1'),
                            allow_text_in_image=bool(data.get('allowTextInImage', False))
                        )

                        # 处理输入图片
                        all_reference_images = []
                        if type_specific_references:
                            all_reference_images.extend(type_specific_references)

                        input_images = services['image_processor'].prepare_input_images(
                            data.get('productImages', []),
                            all_reference_images,
                            max_images=10
                        )

                        print(f"🔄 线程 {index + 1} 调用AI模型生成图片...")
                        logger.info(f"线程 {index + 1} 调用图片生成服务: {data.get('selectedModel', 'nano-banana')}")

                        # 生成图片 - 使用管理器根据模型选择服务

                        image_data = services['image_generator_manager'].generate_image(
                            prompt=prompt,
                            input_images=input_images,
                            model=data.get('selectedModel', 'nano-banana'),
                            size=data.get('selectedSize', '1024x1024'),
                            ratio=data.get('selectedRatio', '1:1')
                        )

                        print(f"✅ 线程 {index + 1} 图片生成完成，正在保存...")
                        logger.info(f"线程 {index + 1} 图片生成成功，开始保存文件")

                        # 保存图片
                        save_result = services['image_processor'].save_generated_image(
                            image_data,
                            f"{task_id}_{image_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{index}",
                            oss_uploader=services['oss_uploader']
                        )

                        filename = save_result['filename']
                        image_url = save_result['url']
                        storage_type = save_result['storage']

                        print(f"💾 线程 {index + 1} 图片已保存: {filename} ({storage_type})")
                        logger.info(f"线程 {index + 1} 图片保存成功: {filename}, 存储: {storage_type}")

                        # 保存到数据库
                        # 获取任务的user_id
                        task_obj = db.session.query(GenerationTask).filter_by(task_id=task_id).first()
                        user_id = task_obj.user_id if task_obj else None

                        generated_image = GeneratedImage(
                            task_id=task_id,
                            user_id=user_id,
                            image_type=image_type,
                            filename=filename,
                            image_url=image_url,
                            storage_type=storage_type,
                            prompt_used=prompt,
                            model_used=data.get('selectedModel', 'nano-banana'),
                            created_at=datetime.utcnow()
                        )
                        db.session.add(generated_image)
                        db.session.commit()

                        # 扣除金币
                        from services.coin_service import CoinService
                        settings = CoinService.get_coin_settings()
                        coin_cost = settings['per_image']
                        success, message = CoinService.deduct_coins(
                            user_id=user_id,
                            amount=coin_cost,
                            task_id=task_id,
                            description=f'生成{image_type}图片消耗{coin_cost}金币'
                        )
                        if not success:
                            logger.warning(f"金币扣除失败: {message}")

                        # 将结果放入队列
                        result_queue.put({
                            'type': 'success',
                            'index': index,
                            'image_type': image_type,
                            'image_data': generated_image.to_dict()
                        })

                except Exception as e:
                    logger.error(f"并行生成图片失败 {image_type}: {str(e)}")
                    # 将错误信息放入队列
                    result_queue.put({
                        'type': 'error',
                        'index': index,
                        'image_type': image_type,
                        'error': str(e)
                    })

            def generate_stream():
                """生成器函数，用于流式响应"""
                with app.app_context():  # 确保在应用上下文中执行
                    try:
                        services = get_services()
                        generated_count = 0
                        total_images = len(data['selectedImageTypes'])

                        # 发送初始状态
                        yield f"data: {json.dumps({'type': 'status', 'task_id': task_id, 'status': 'started', 'progress': 0})}\n\n"

                        # 创建结果队列
                        result_queue = queue.Queue()

                        # 使用ThreadPoolExecutor进行并行处理
                        with ThreadPoolExecutor(max_workers=min(total_images, 3)) as executor:
                            # 提交所有图片生成任务
                            futures = []
                            for i, image_type in enumerate(data['selectedImageTypes']):
                                future = executor.submit(
                                    generate_single_image,
                                    image_type, i, result_queue, services, data, task_id
                                )
                                futures.append(future)

                            # 监控任务完成情况
                            completed_tasks = 0
                            start_time = time.time()

                            while completed_tasks < total_images:
                                try:
                                    # 从队列中获取结果，设置超时避免无限等待
                                    result = result_queue.get(timeout=1.0)
                                    completed_tasks += 1

                                    if result['type'] == 'success':
                                        generated_count += 1

                                        # 发送生成完成的图片信息
                                        image_info = {
                                            'type': 'image_complete',
                                            'task_id': task_id,
                                            'image': result['image_data'],
                                            'progress': int((completed_tasks / total_images) * 100)
                                        }
                                        yield f"data: {json.dumps(image_info)}\n\n"

                                    elif result['type'] == 'error':
                                        # 发送错误信息
                                        error_info = {
                                            'type': 'image_error',
                                            'task_id': task_id,
                                            'image_type': result['image_type'],
                                            'error': result['error'],
                                            'progress': int((completed_tasks / total_images) * 100)
                                        }
                                        yield f"data: {json.dumps(error_info)}\n\n"

                                    # 发送进度更新
                                    progress_info = {
                                        'type': 'progress',
                                        'task_id': task_id,
                                        'completed': completed_tasks,
                                        'total': total_images,
                                        'progress': int((completed_tasks / total_images) * 100)
                                    }
                                    yield f"data: {json.dumps(progress_info)}\n\n"

                                except queue.Empty:
                                    # 队列为空，继续等待
                                    # 检查是否有任务超时（可选的超时保护）
                                    elapsed_time = time.time() - start_time
                                    if elapsed_time > 300:  # 5分钟超时
                                        logger.warning(f"任务 {task_id} 执行超时")
                                        break
                                    continue

                        # 更新任务状态
                        task_obj = db.session.query(GenerationTask).filter_by(task_id=task_id).first()
                        if task_obj:
                            task_obj.status = 'completed' if generated_count > 0 else 'failed'
                            task_obj.progress = 100
                            db.session.commit()

                        # 发送完成状态
                        completion_info = {
                            'type': 'complete',
                            'task_id': task_id,
                            'status': task_obj.status if task_obj else 'completed',
                            'generated_count': generated_count,
                            'total_count': total_images
                        }
                        yield f"data: {json.dumps(completion_info)}\n\n"

                        print(f"🎉 并行生成任务完成！成功生成 {generated_count}/{total_images} 张图片")
                        logger.info(f"并行生成任务完成：{generated_count}/{total_images}")

                    except Exception as e:
                        logger.error(f"流式生成错误: {str(e)}")
                        # 更新任务状态为失败
                        task_obj = db.session.query(GenerationTask).filter_by(task_id=task_id).first()
                        if task_obj:
                            task_obj.status = 'failed'
                            task_obj.error_message = str(e)
                            db.session.commit()

                        error_info = {
                            'type': 'error',
                            'task_id': task_id,
                            'error': str(e)
                        }
                        yield f"data: {json.dumps(error_info)}\n\n"

            return Response(
                generate_stream(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )

        except Exception as e:
            logger.error(f"流式生成接口错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/task-status/<task_id>', methods=['GET'])
    def get_task_status(task_id):
        """获取任务状态"""
        try:
            task = GenerationTask.query.filter_by(task_id=task_id).first()
            if not task:
                return jsonify({'error': '任务不存在'}), 404

            # 获取已生成的图片
            generated_images = GeneratedImage.query.filter_by(task_id=task_id).all()

            return jsonify({
                'task_id': task_id,
                'status': task.status,
                'progress': task.progress,
                'generated_count': len(generated_images),
                'total_count': task.total_images,
                'images': [img.to_dict() for img in generated_images],
                'error_message': task.error_message
            })

        except Exception as e:
            logger.error(f"获取任务状态错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/regenerate-image', methods=['POST'])
    def regenerate_image():
        """
        重新生成图片接口
        支持基于上下文的优化
        """
        try:
            data = request.json

            # 验证必需字段
            if 'original_image_id' not in data:
                return jsonify({'error': '缺少原始图片ID'}), 400

            original_image = GeneratedImage.query.get(data['original_image_id'])
            if not original_image:
                return jsonify({'error': '原始图片不存在'}), 404

            # 获取上下文信息
            services = get_services()
            context = services['context_manager'].get_generation_context(original_image.task_id)

            # 获取参考图片（从referenceImagesByType中提取当前类型的参考图）
            image_type = original_image.image_type
            reference_images_for_type = data.get('referenceImagesByType', {}).get(image_type, [])

            # 构建新的提示词（结合用户修改和上下文）
            new_prompt = services['prompt_builder'].build_rework_prompt(
                original_prompt=original_image.prompt_used,
                user_modifications={'prompt_modifications': data.get('mainPrompt', '')},
                context=context,
                reference_images=reference_images_for_type,
                original_image_info={'type': image_type},
                previous_image_url=original_image.image_url
            )

            logger.info(f"重新生成提示词构建完成，包含 {len(reference_images_for_type)} 张参考图")

            # 创建重新生成任务
            rework_task = GenerationTask(
                task_id=str(uuid.uuid4()),
                user_id=request.user_id,  # 关联用户
                user_input=json.dumps(data),
                status='pending',
                parent_task_id=original_image.task_id,
                created_at=datetime.utcnow()
            )
            db.session.add(rework_task)
            db.session.commit()

            # 异步处理重新生成
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(process_rework_task, rework_task.task_id, original_image.id, new_prompt)

            return jsonify({
                'success': True,
                'task_id': rework_task.task_id,
                'message': '图片重新生成任务已启动'
            })

        except Exception as e:
            logger.error(f"重新生成图片错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cancel-task/<task_id>', methods=['POST'])
    def cancel_task(task_id):
        """
        终止生成任务
        """
        try:
            task = GenerationTask.query.filter_by(task_id=task_id).first()
            if not task:
                return jsonify({'error': '任务不存在'}), 404

            if task.status in ['completed', 'failed']:
                return jsonify({'error': '任务已完成，无法终止'}), 400

            # 更新任务状态为已取消
            task.status = 'cancelled'
            task.error_message = '用户手动终止'
            db.session.commit()

            logger.info(f"任务已终止: {task_id}")

            return jsonify({
                'success': True,
                'message': '任务已成功终止',
                'task_id': task_id
            })

        except Exception as e:
            logger.error(f"终止任务错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/image/<filename>')
    def serve_generated_image(filename):
        """提供生成的图片文件"""
        try:
            return send_from_directory('generated_images', filename)
        except Exception as e:
            logger.error(f"提供生成图片文件错误: {str(e)}")
            return jsonify({'error': '生成图片不存在'}), 404

    @app.route('/api/upload/<filename>')
    def serve_uploaded_image(filename):
        """提供上传的图片文件"""
        try:
            import os
            # 获取uploads目录的绝对路径
            uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

            # 检查文件是否存在
            file_path = os.path.join(uploads_dir, filename)
            if not os.path.exists(file_path):
                logger.error(f"图片文件不存在: {file_path}")
                return jsonify({'error': f'图片文件不存在: {filename}'}), 404

            logger.info(f"提供图片文件: {file_path}")
            response = send_from_directory(uploads_dir, filename)
            # 添加必要的响应头
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Cache-Control'] = 'public, max-age=3600'
            return response
        except Exception as e:
            logger.error(f"提供上传图片文件错误: {str(e)}")
            return jsonify({'error': f'服务器错误: {str(e)}'}), 500

    # 添加备用的静态文件路由
    @app.route('/uploads/<filename>')
    def serve_uploaded_image_alt(filename):
        """备用的图片文件服务路由"""
        try:
            import os
            uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            file_path = os.path.join(uploads_dir, filename)

            if not os.path.exists(file_path):
                logger.error(f"备用路由 - 图片文件不存在: {file_path}")
                return jsonify({'error': f'图片文件不存在: {filename}'}), 404

            logger.info(f"备用路由 - 提供图片文件: {file_path}")
            response = send_from_directory(uploads_dir, filename)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            logger.error(f"备用路由 - 提供图片文件错误: {str(e)}")
            return jsonify({'error': f'服务器错误: {str(e)}'}), 500

    # 添加调试路由
    @app.route('/api/debug/uploads')
    def debug_uploads():
        """调试路由：列出uploads目录中的所有文件"""
        try:
            import os
            uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

            if not os.path.exists(uploads_dir):
                return jsonify({
                    'error': 'uploads目录不存在',
                    'uploads_dir': uploads_dir
                })

            files = []
            for filename in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, filename)
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'url': f'/api/upload/{filename}',
                        'alt_url': f'/uploads/{filename}'
                    })

            return jsonify({
                'uploads_dir': uploads_dir,
                'files_count': len(files),
                'files': files
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/upload-image', methods=['POST'])
    @token_required
    def upload_image():
        """上传图片接口"""
        try:
            if 'image' not in request.files:
                return jsonify({'error': '没有图片文件'}), 400

            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': '未选择文件'}), 400

            services = get_services()

            # 使用 image_processor 统一处理上传（自动根据配置决定OSS或本地）
            # 如果配置了 OSS_ENABLED=true 且 oss_uploader 可用，会自动上传到 OSS
            # 如果 OSS 上传失败（3次重试后）或 OSS_ENABLED=false，会自动回退到本地存储
            result = services['image_processor'].save_uploaded_image(
                file,
                oss_uploader=services['oss_uploader'] if services.get('oss_uploader') else None
            )

            logger.info(f"图片保存成功: {result['filename']}, 存储方式: {result['storage']}")

            return jsonify({
                'success': True,
                'filename': result['filename'],
                'url': result['url'],
                'id': result['filename'],
                'storage': result['storage']
            })

        except Exception as e:
            logger.error(f"上传图片错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/save-history', methods=['POST'])
    @token_required
    def save_generation_history():
        """保存生成历史记录（支持创建和更新）"""
        logger.info(f"🔵 收到保存历史记录请求 - 用户ID: {request.user_id}")
        try:
            data = request.json
            logger.info(f"📝 保存历史记录数据: {json.dumps(data, ensure_ascii=False)[:500]}")

            # 验证必需字段
            required_fields = ['taskId', 'generationParams']
            for field in required_fields:
                if field not in data:
                    logger.error(f"❌ 缺少必需字段: {field}")
                    return jsonify({'error': f'缺少必需字段: {field}'}), 400

            params = data['generationParams']

            # 从产品信息中获取标题
            product_form = params.get('productForm', {})
            title = product_form.get('title', '未命名任务')
            if isinstance(product_form, str):
                title = product_form

            logger.info(f"📋 任务标题: {title}, TaskID: {data['taskId']}")

            # 查找是否已存在该任务的历史记录
            history = GenerationHistory.query.filter_by(
                user_id=request.user_id,
                task_id=data['taskId']
            ).first()

            if history:
                # 更新现有记录
                history.title = title
                history.product_form = json.dumps(product_form) if isinstance(product_form, dict) else product_form
                history.selected_image_types = json.dumps(params.get('selectedImageTypes', []))
                history.main_prompt = params.get('mainPrompt')
                history.product_images = json.dumps(params.get('productImages', []))
                history.reference_images_by_type = json.dumps(params.get('referenceImagesByType', {}))
                history.competitors = json.dumps(params.get('competitors', []))
                history.selected_size = params.get('selectedSize')
                history.selected_ratio = params.get('selectedRatio')
                history.selected_model = params.get('selectedModel')
                history.generated_image_count = data.get('generatedImageCount', 0)
                history.success_count = data.get('successCount', 0)
                history.generation_time = data.get('generationTime')
                history.user_notes = data.get('userNotes')
                history.updated_at = datetime.utcnow()
                message = '历史记录更新成功'
            else:
                # 创建新记录
                history = GenerationHistory(
                    user_id=request.user_id,
                    task_id=data['taskId'],
                    title=title,
                    is_pinned=False,
                    product_form=json.dumps(product_form) if isinstance(product_form, dict) else product_form,
                    selected_image_types=json.dumps(params.get('selectedImageTypes', [])),
                    main_prompt=params.get('mainPrompt'),
                    product_images=json.dumps(params.get('productImages', [])),
                    reference_images_by_type=json.dumps(params.get('referenceImagesByType', {})),
                    competitors=json.dumps(params.get('competitors', [])),
                    selected_size=params.get('selectedSize'),
                    selected_ratio=params.get('selectedRatio'),
                    selected_model=params.get('selectedModel'),
                    generated_image_count=data.get('generatedImageCount', 0),
                    success_count=data.get('successCount', 0),
                    generation_time=data.get('generationTime'),
                    user_notes=data.get('userNotes')
                )
                db.session.add(history)
                message = '历史记录保存成功'

            db.session.commit()

            logger.info(f"✅ 历史记录保存成功 - ID: {history.id}, 标题: {history.title}")

            return jsonify({
                'success': True,
                'history_id': history.id,
                'message': message,
                'history': history.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 保存历史记录错误: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @app.route('/api/history', methods=['GET'])
    @token_required
    def get_generation_history():
        """获取生成历史记录列表"""
        try:
            # 分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '')  # 标题搜索

            # 构建查询 - 只查询当前用户的历史记录
            query = GenerationHistory.query.filter_by(user_id=request.user_id)

            # 标题搜索
            if search:
                query = query.filter(GenerationHistory.title.like(f'%{search}%'))

            # 先按置顶排序，再按创建时间倒序排列
            query = query.order_by(
                GenerationHistory.is_pinned.desc(),
                GenerationHistory.created_at.desc()
            )

            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            history_list = []
            for history in pagination.items:
                history_dict = history.to_dict()
                # 添加任务状态信息
                if history.task:
                    history_dict['task_status'] = history.task.status
                    history_dict['task_progress'] = history.task.progress

                history_list.append(history_dict)

            return jsonify({
                'success': True,
                'history': history_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            })

        except Exception as e:
            logger.error(f"获取历史记录错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/history/<int:history_id>', methods=['GET'])
    @token_required
    def get_history_detail(history_id):
        """获取历史记录详情"""
        try:
            history = GenerationHistory.query.get(history_id)
            if not history:
                return jsonify({'error': '历史记录不存在'}), 404

            # 验证权限
            if history.user_id != request.user_id:
                return jsonify({'error': '无权访问此历史记录'}), 403

            # 获取该历史记录对应的所有生成图片
            generated_images = GeneratedImage.query.filter_by(
                task_id=history.task_id,
                user_id=request.user_id
            ).order_by(GeneratedImage.created_at.desc()).all()

            history_dict = history.to_dict()
            history_dict['generated_images'] = [img.to_dict() for img in generated_images]

            return jsonify({
                'success': True,
                'history': history_dict
            })

        except Exception as e:
            logger.error(f"获取历史记录详情错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/history/<int:history_id>', methods=['PUT'])
    @token_required
    def update_history(history_id):
        """更新历史记录（标题、置顶、用户评分、备注等）"""
        try:
            history = GenerationHistory.query.get(history_id)
            if not history:
                return jsonify({'error': '历史记录不存在'}), 404

            # 验证权限
            if history.user_id != request.user_id:
                return jsonify({'error': '无权修改此历史记录'}), 403

            data = request.json

            # 更新允许修改的字段
            if 'title' in data:
                history.title = data['title']
            if 'isPinned' in data:
                history.is_pinned = data['isPinned']
            if 'userRating' in data:
                history.user_rating = data['userRating']
            if 'userNotes' in data:
                history.user_notes = data['userNotes']
            if 'isFavorite' in data:
                history.is_favorite = data['isFavorite']

            history.updated_at = datetime.utcnow()
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '历史记录更新成功',
                'history': history.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"更新历史记录错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/history/<int:history_id>', methods=['DELETE'])
    @token_required
    def delete_history(history_id):
        """删除历史记录"""
        try:
            history = GenerationHistory.query.get(history_id)
            if not history:
                return jsonify({'error': '历史记录不存在'}), 404

            # 验证权限
            if history.user_id != request.user_id:
                return jsonify({'error': '无权删除此历史记录'}), 403

            db.session.delete(history)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '历史记录删除成功'
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"删除历史记录错误: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def process_generation_task(task_id, data):
        """
        处理图片生成任务的核心逻辑
        """
        try:
            services = get_services()

            with app.app_context():
                task = GenerationTask.query.filter_by(task_id=task_id).first()
                task.status = 'processing'
                task.total_images = len(data['selectedImageTypes'])
                task.progress = 0
                db.session.commit()

                generated_count = 0

                for image_type in data['selectedImageTypes']:
                    try:
                        # 检查任务是否被终止
                        task = GenerationTask.query.filter_by(task_id=task_id).first()
                        if task.status == 'cancelled':
                            logger.info(f"任务已被终止: {task_id}")
                            return

                        # 构建针对特定图片类型的提示词
                        # 获取该图片类型的特定参考图
                        type_specific_references = data.get('referenceImagesByType', {}).get(image_type, [])
                        logger.info(
                            f"🎯 处理图片类型: {image_type}, 获取到 {len(type_specific_references)} 张类型特定参考图")

                        prompt = services['prompt_builder'].build_prompt(
                            product_form=data['productForm'],
                            image_type=image_type,
                            main_prompt=data['mainPrompt'],
                            reference_images=[],  # 不再使用全局参考图
                            competitors=data.get('competitors', []),
                            type_specific_references=type_specific_references,
                            allow_text_in_image=bool(data.get('allowTextInImage', False))
                        )

                        # 处理输入图片（Nano Banana最多支持10张）
                        # 为当前图片类型准备图片：产品图片 + 类型特定参考图
                        all_reference_images = []
                        if type_specific_references:
                            all_reference_images.extend(type_specific_references)

                        input_images = services['image_processor'].prepare_input_images(
                            data.get('productImages', []),
                            all_reference_images,
                            max_images=10
                        )

                        # 调用图片生成服务 - 使用管理器根据模型选择服务
                        generated_image_data = services['image_generator_manager'].generate_image(
                            prompt=prompt,
                            input_images=input_images,
                            model='nano-banana',
                            size=data.get('selectedSize', '2000x2000'),
                            ratio=data.get('selectedRatio', '1:1')
                        )

                        # 保存生成的图片
                        save_result = services['image_processor'].save_generated_image(
                            generated_image_data,
                            f"{task_id}_{image_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png",
                            oss_uploader=services['oss_uploader']
                        )

                        filename = save_result['filename']
                        image_url = save_result['url']
                        storage_type = save_result['storage']

                        logger.info(f"生成图片保存成功: {filename}, 存储: {storage_type}")

                        # 记录到数据库
                        generated_image = GeneratedImage(
                            task_id=task_id,
                            user_id=task.user_id,
                            image_type=image_type,
                            filename=filename,
                            image_url=image_url,
                            storage_type=storage_type,
                            prompt_used=prompt,
                            model_used='nano-banana',
                            created_at=datetime.utcnow()
                        )
                        db.session.add(generated_image)

                        generated_count += 1
                        task.progress = int((generated_count / task.total_images) * 100)
                        db.session.commit()

                        logger.info(f"成功生成图片: {image_type} for task {task_id}")

                    except Exception as e:
                        logger.error(f"生成图片失败 {image_type}: {str(e)}")
                        continue

                # 更新任务状态
                if generated_count > 0:
                    task.status = 'completed'
                    task.progress = 100
                else:
                    task.status = 'failed'
                    task.error_message = '所有图片生成都失败了'

                db.session.commit()
                logger.info(f"任务 {task_id} 完成，生成了 {generated_count} 张图片")

        except Exception as e:
            logger.error(f"处理生成任务错误: {str(e)}")
            with app.app_context():
                task = GenerationTask.query.filter_by(task_id=task_id).first()
                if task:
                    task.status = 'failed'
                    task.error_message = str(e)
                    db.session.commit()

    def process_rework_task(task_id, original_image_id, new_prompt):
        """
        处理图片重新生成任务
        """
        try:
            services = get_services()

            with app.app_context():
                # 重新查询原始图片以避免会话问题
                original_image = GeneratedImage.query.get(original_image_id)
                if not original_image:
                    raise Exception(f"原始图片不存在: {original_image_id}")

                task = GenerationTask.query.filter_by(task_id=task_id).first()
                task.status = 'processing'
                task.total_images = 1
                task.progress = 0
                db.session.commit()

                # 从任务数据中获取产品图片、参考图片和上一次生成的图片
                task_data = json.loads(task.user_input)
                product_images = task_data.get('productImages', [])
                image_type = original_image.image_type
                reference_images = task_data.get('referenceImagesByType', {}).get(image_type, [])
                previous_image_url = original_image.image_url

                # 准备输入图片：产品图 + 参考图 + 上一次生成的图（用于上下文）
                all_input_images = []

                # 1. 产品原图（最重要，放在最前面）
                if product_images:
                    all_input_images.extend(product_images)
                    logger.info(f"重新生成 - 包含 {len(product_images)} 张产品原图")

                # 2. 参考图（用户提供的风格参考）
                if reference_images:
                    all_input_images.extend(reference_images)
                    logger.info(f"重新生成 - 包含 {len(reference_images)} 张参考图")

                # 3. 上一次生成的图（可选，仅作为上下文）
                if previous_image_url:
                    all_input_images.append({
                        'url': previous_image_url,
                        'storage': original_image.storage_type or 'oss',
                        'filename': original_image.filename,
                        'description': '上一次生成的图片（仅供参考）'
                    })
                    logger.info(f"重新生成 - 包含上一次生成的图片作为上下文")

                # 处理输入图片为base64
                input_images_base64 = services['image_processor'].prepare_input_images(
                    product_images,
                    reference_images,
                    max_images=15  # 增加最大图片数以容纳所有类型
                )

                logger.info(f"重新生成 - 总共准备了 {len(input_images_base64)} 张输入图片（产品图+参考图）")

                # 调用图片生成服务重新生成 - 使用管理器根据模型选择服务
                generated_image_data = services['image_generator_manager'].generate_image(
                    prompt=new_prompt,
                    input_images=input_images_base64,
                    model=task_data.get('selectedModel', 'nano-banana')
                )

                # 保存新生成的图片
                save_result = services['image_processor'].save_generated_image(
                    generated_image_data,
                    f"rework_{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png",
                    oss_uploader=services['oss_uploader']
                )

                filename = save_result['filename']
                image_url = save_result['url']
                storage_type = save_result['storage']

                logger.info(f"重新生成图片保存成功: {filename}, 存储: {storage_type}")

                # 记录到数据库
                new_image = GeneratedImage(
                    task_id=task_id,
                    image_type=original_image.image_type,
                    filename=filename,
                    image_url=image_url,
                    storage_type=storage_type,
                    prompt_used=new_prompt,
                    model_used='nano-banana',
                    parent_image_id=original_image.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_image)

                # 更新上下文记忆
                services['context_manager'].update_context(
                    original_image.task_id,
                    original_image,
                    new_image,
                    new_prompt
                )

                task.status = 'completed'
                task.progress = 100
                db.session.commit()

                logger.info(f"重新生成图片成功: {filename}")
                logger.info(f"重新生成图片完成: task {task_id}")

        except Exception as e:
            logger.error(f"重新生成图片错误: {str(e)}")
            with app.app_context():
                task = GenerationTask.query.filter_by(task_id=task_id).first()
                if task:
                    task.status = 'failed'
                    task.error_message = str(e)
                    db.session.commit()

    return app


# 创建应用实例
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"启动Amazon AIGC助手后端服务...")
    print(f"运行地址: http://{host}:{port}")
    print(f"调试模式: {debug}")

    app.run(host=host, port=port, debug=debug)
