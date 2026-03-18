from typing import Dict, List, Optional, Any
import os
import sys
import sqlite3
import shutil
import threading
import hashlib
import queue
from datetime import datetime
from PySide6.QtCore import (Qt, QSize, QSettings, QDateTime, QTimer, 
                         Signal, QThread, QModelIndex, QEvent, QObject, Slot)
from PySide6.QtGui import (QIcon, QPixmap, QKeySequence, QClipboard, 
                        QGuiApplication, QPainter, QPen, 
                        QColor, QPixmapCache, QAction)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QTextEdit, QMessageBox, QFileDialog, QDialog, 
                            QGroupBox, QFormLayout, QSizePolicy, QMenu, QMenuBar,
                            QTabWidget, QListWidget, QListWidgetItem, QSplitter, 
                            QInputDialog, QHeaderView, QAbstractItemView, QDialogButtonBox,
                            QDateTimeEdit, QStatusBar, QScrollArea, QProgressDialog, QWidget,
                            QSpinBox)

class ProjectInfo:
    """项目信息元数据（集中管理所有项目相关信息）"""
    VERSION = "3.16.9"
    BUILD_DATE = "2026-03-18"
    AUTHOR = "杜玛"
    LICENSE = "GNU Affero General Public License v3.0"
    COPYRIGHT = "© 永久 杜玛"
    URL = "https://github.com/duma520/ImageManagerApp"
    MAINTAINER_EMAIL = "不提供"
    NAME = "ImageManagerApp"
    DESCRIPTION = "ImageManagerApp"
    
    @classmethod
    def get_version_string(cls) -> str:
        """获取版本信息字符串"""
        return f"{cls.NAME} v{cls.VERSION} ({cls.BUILD_DATE})"
    
    @classmethod
    def get_copyright_string(cls) -> str:
        """获取版权信息字符串"""
        return f"{cls.COPYRIGHT} {cls.AUTHOR}"
    
    @classmethod
    def get_full_info(cls) -> str:
        """获取完整的项目信息"""
        info = [
            f"{cls.NAME} v{cls.VERSION}",
            f"构建日期: {cls.BUILD_DATE}",
            f"作者: {cls.AUTHOR}",
            f"许可证: {cls.LICENSE}",
            f"版权: {cls.COPYRIGHT}",
            f"项目主页: {cls.URL}",
            f"维护者邮箱: {cls.MAINTAINER_EMAIL}",
            f"描述: {cls.DESCRIPTION}"
        ]
        return "\n".join(info)
    
    @classmethod
    def get_about_html(cls) -> str:
        """获取关于信息的HTML格式"""
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }}
                h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .info {{ margin: 10px 0; }}
                .label {{ color: #7f8c8d; font-weight: bold; width: 100px; display: inline-block; }}
                .value {{ color: #2c3e50; }}
                .version {{ font-size: 24px; color: #3498db; margin: 20px 0; }}
                .copyright {{ margin-top: 30px; color: #95a5a6; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <h2>{cls.NAME}</h2>
            <div class="version">{cls.VERSION}</div>
            <div class="info"><span class="label">构建日期</span><span class="value">{cls.BUILD_DATE}</span></div>
            <div class="info"><span class="label">作者</span><span class="value">{cls.AUTHOR}</span></div>
            <div class="info"><span class="label">许可证</span><span class="value">{cls.LICENSE}</span></div>
            <div class="info"><span class="label">项目主页</span><span class="value"><a href="{cls.URL}">{cls.URL}</a></span></div>
            <div class="info"><span class="label">描述</span><span class="value">{cls.DESCRIPTION}</span></div>
            <div class="copyright">{cls.COPYRIGHT}</div>
        </body>
        </html>
        """
        return html
    
    @classmethod
    def check_for_updates(cls) -> bool:
        """
        检查是否有新版本
        返回True表示有新版本，False表示已是最新
        """
        try:
            import requests
            # 这里可以实现从GitHub检查最新版本的逻辑
            url = f"https://api.github.com/repos/duma520/{cls.NAME}/releases/latest"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                latest_version = response.json().get('tag_name', '').lstrip('v')
                current = [int(x) for x in cls.VERSION.split('.')]
                latest = [int(x) for x in latest_version.split('.')]
                return latest > current
        except ImportError:
            # 如果没有requests模块，静默失败
            pass
        except Exception:
            # 其他异常也静默处理
            pass
        return False
    
    @classmethod
    def get_update_message(cls) -> str:
        """获取更新提示信息"""
        if cls.check_for_updates():
            return f"发现新版本！当前版本: {cls.VERSION}，请访问 {cls.URL}/releases 下载最新版本。"
        return f"当前已是最新版本: {cls.VERSION}"
    
    @classmethod
    def save_to_file(cls, filepath: str):
        """将项目信息保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cls.get_full_info())
    
    @classmethod
    def get_database_info(cls) -> Dict[str, str]:
        """获取数据库相关信息"""
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        users_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users")
        
        return {
            'database_dir': db_dir,
            'backup_dir': backup_dir,
            'users_dir': users_dir,
            'database_pattern': 'user_*.db',
            'hash_algorithm': 'md5',
            'hash_length': '16'
        }
    
    @classmethod
    def get_system_requirements(cls) -> Dict[str, str]:
        """获取系统要求"""
        return {
            'python': '>=3.8',
            'pyside6': '>=6.0.0',
            'requests': '>=2.25.0 (可选)',
            'pypinyin': '>=0.50.0 (可选)',
            'memory': '>=512MB',
            'disk': '>=100MB'
        }
    
    @classmethod
    def print_info(cls):
        """打印项目信息到控制台"""
        print("=" * 60)
        print(cls.get_full_info())
        print("=" * 60)
    
    @classmethod
    def to_dict(cls) -> Dict[str, str]:
        """将所有信息转换为字典格式"""
        return {
            'name': cls.NAME,
            'version': cls.VERSION,
            'build_date': cls.BUILD_DATE,
            'author': cls.AUTHOR,
            'license': cls.LICENSE,
            'copyright': cls.COPYRIGHT,
            'url': cls.URL,
            'maintainer_email': cls.MAINTAINER_EMAIL,
            'description': cls.DESCRIPTION
        }
    
    @classmethod
    def get_app_dir(cls) -> str:
        """获取应用程序目录"""
        return os.path.dirname(os.path.abspath(__file__))
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录结构"""
        dirs = [
            os.path.join(cls.get_app_dir(), "data"),
            os.path.join(cls.get_app_dir(), "backups"),
            os.path.join(cls.get_app_dir(), "users"),
            os.path.join(cls.get_app_dir(), "logs"),
            os.path.join(cls.get_app_dir(), "temp")
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        return dirs
    
    @classmethod
    def get_log_file(cls) -> str:
        """获取日志文件路径"""
        log_dir = os.path.join(cls.get_app_dir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m')}.log")
    
    @classmethod
    def get_temp_dir(cls) -> str:
        """获取临时目录"""
        temp_dir = os.path.join(cls.get_app_dir(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    @classmethod
    def get_user_data_dir(cls, username: str) -> str:
        """获取用户数据目录"""
        user_dir = os.path.join(cls.get_app_dir(), "users", username)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    @classmethod
    def get_user_db_path(cls, username: str) -> str:
        """获取用户数据库路径"""
        return os.path.join(cls.get_app_dir(), f"user_{username}.db")
    
    @classmethod
    def get_user_images_dir(cls, username: str) -> str:
        """获取用户图片存储目录"""
        images_dir = os.path.join(cls.get_app_dir(), "data", f"user_{username}")
        os.makedirs(images_dir, exist_ok=True)
        return images_dir
    
    @classmethod
    def cleanup_temp_files(cls, max_age_hours: int = 24):
        """清理临时文件"""
        import time
        temp_dir = cls.get_temp_dir()
        current_time = time.time()
        
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_hours * 3600:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass


# 线程安全的数据库连接池类
class DatabasePool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = {}  # 按线程ID存储连接
        self.lock = threading.Lock()
    
    def get_connection(self):
        """获取当前线程的数据库连接"""
        thread_id = threading.get_ident()
        
        with self.lock:
            if thread_id in self.connections:
                # 检查连接是否有效
                conn = self.connections[thread_id]
                try:
                    conn.execute("SELECT 1").fetchone()
                    return conn
                except:
                    # 连接已失效，创建新连接
                    pass
            
            # 创建新连接
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self.connections[thread_id] = conn
            return conn
    
    def return_connection(self, conn):
        """连接不需要返回，因为我们是按线程持有"""
        pass
    
    def close_all(self):
        """关闭所有线程的连接"""
        with self.lock:
            for thread_id, conn in self.connections.items():
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
    
    def close_thread_connection(self):
        """关闭当前线程的连接"""
        thread_id = threading.get_ident()
        with self.lock:
            if thread_id in self.connections:
                try:
                    self.connections[thread_id].close()
                except:
                    pass
                del self.connections[thread_id]

# 图片保存工作线程 - 优化版本
class ImageSaveThread(QThread):
    finished = Signal(bool, object)  # 成功标志和结果数据
    
    def __init__(self, db_pool, save_func, *args):
        super().__init__()
        self.db_pool = db_pool
        self.save_func = save_func
        self.args = args
    
    def run(self):
        try:
            result = self.save_func(self.db_pool, *self.args)
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))
        finally:
            # 清理线程的数据库连接
            self.db_pool.close_thread_connection()

# 图片加载线程
class ImageLoadThread(QThread):
    image_loaded = Signal(object, str)  # pixmap, file_path
    
    def __init__(self, file_path, target_size=None):
        super().__init__()
        self.file_path = file_path
        self.target_size = target_size
        self._is_running = True
    
    def run(self):
        if not self._is_running:
            return
            
        if os.path.exists(self.file_path):
            pixmap = QPixmap(self.file_path)
            if not pixmap.isNull() and self.target_size and self._is_running:
                pixmap = pixmap.scaled(
                    self.target_size.width(), 
                    self.target_size.height(), 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
            if self._is_running:
                self.image_loaded.emit(pixmap, self.file_path)
    
    def stop(self):
        self._is_running = False

# 数据库初始化
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 启用WAL模式
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # 创建图片表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        tags TEXT,
        file_path TEXT UNIQUE NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建索引
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_images_category ON images(category)
    ''')
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_images_create_time ON images(create_time)
    ''')
    
    # 创建搜索虚拟表（支持中文拼音搜索）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images_fts'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS images_fts USING fts5(
            name, description, category, tags, 
            tokenize="unicode61 remove_diacritics 2"
        )
        ''')
    
    conn.commit()
    return conn

# 备份管理类
class BackupManager:
    def __init__(self, app_dir, max_backups=30):
        self.backup_dir = os.path.join(app_dir, "backups")
        self.max_backups = max_backups
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, db_path, backup_type="manual"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{backup_type}_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # 使用WAL模式备份
        src_conn = sqlite3.connect(db_path)
        dst_conn = sqlite3.connect(backup_path)
        
        with dst_conn:
            src_conn.backup(dst_conn, pages=1)
        
        src_conn.close()
        dst_conn.close()
        
        # 清理旧备份
        self.cleanup_old_backups()
        
        return backup_path
    
    def cleanup_old_backups(self):
        backups = self.get_all_backups()
        if len(backups) > self.max_backups:
            backups_to_remove = backups[self.max_backups:]
            for backup in backups_to_remove:
                try:
                    os.remove(backup['filepath'])
                except Exception as e:
                    print(f"Error removing backup {backup['filepath']}: {e}")
    
    def get_all_backups(self):
        backups = []
        if not os.path.exists(self.backup_dir):
            return backups
            
        for filename in os.listdir(self.backup_dir):
            if filename.endswith(".db"):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                
                # 解析备份类型和时间
                parts = filename.split('_')
                if len(parts) >= 3:
                    backup_type = parts[0]
                    date_part = parts[1]
                    time_part = parts[2].split('.')[0]
                    
                    try:
                        dt = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                        backups.append({
                            'filename': filename,
                            'filepath': filepath,
                            'type': backup_type,
                            'size': stat.st_size,
                            'time': dt
                        })
                    except ValueError:
                        continue
        
        # 按时间降序排序
        backups.sort(key=lambda x: x['time'], reverse=True)
        return backups
    
    def restore_backup(self, backup_path, target_path):
        # 先备份当前数据库
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rollback_path = os.path.join(self.backup_dir, f"rollback_before_restore_{timestamp}.db")
        
        if os.path.exists(target_path):
            shutil.copy2(target_path, rollback_path)
        
        # 执行恢复
        src_conn = sqlite3.connect(backup_path)
        dst_conn = sqlite3.connect(target_path)
        
        with dst_conn:
            src_conn.backup(dst_conn, pages=1)
        
        src_conn.close()
        dst_conn.close()
        
        return rollback_path

# 用户管理类
class UserManager:
    def __init__(self, app_dir):
        self.app_dir = app_dir
        self.users_db = os.path.join(app_dir, "users.db")
        self._init_users_db()
    
    def _init_users_db(self):
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
        ''')
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, last_login FROM users ORDER BY username")
        users = cursor.fetchall()
        conn.close()
        return users
    
    def add_user(self, username):
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            
            # 创建用户数据库
            user_db_path = self.get_user_db_path(username)
            init_db(user_db_path)
            
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_user(self, username):
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()
        
        # 删除用户数据库文件
        user_db_path = self.get_user_db_path(username)
        if os.path.exists(user_db_path):
            os.remove(user_db_path)
    
    def update_username(self, old_username, new_username):
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET username=? WHERE username=?", 
                         (new_username, old_username))
            conn.commit()
            
            # 重命名数据库文件
            old_db_path = self.get_user_db_path(old_username)
            new_db_path = self.get_user_db_path(new_username)
            if os.path.exists(old_db_path):
                os.rename(old_db_path, new_db_path)
            
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_last_login(self, username):
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE username=?", (username,))
        conn.commit()
        conn.close()
    
    def get_user_db_path(self, username):
        return ProjectInfo.get_user_db_path(username)
    
    def get_user_images_dir(self, username):
        return ProjectInfo.get_user_images_dir(username)

# 图片管理主窗口
class ImageManagerWindow(QMainWindow):
    logout_requested = Signal()
    PAGE_SIZE = 200  # 每页显示200张图片
    
    def __init__(self, user_manager, username):
        super().__init__()
        self.user_manager = user_manager
        self.username = username
        self.db_path = ProjectInfo.get_user_db_path(username)
        self.backup_manager = BackupManager(ProjectInfo.get_app_dir())
        self.current_image_id = None
        self.save_thread = None
        self.load_thread = None
        self.current_page = 1
        self.total_pages = 1
        self.total_images = 0
        self.current_query = None  # 保存当前搜索条件
        self.PAGE_SIZE = 200  # 默认每页显示200张图片
    
        # 添加设置管理器
        self.settings = QSettings("ImageManager", f"ImageManagerWindow_{username}")
    
        # 从设置中读取每页显示数量
        self.PAGE_SIZE = int(self.settings.value("page_size", 200))
    
        # 初始化数据库连接池
        self.db_pool = DatabasePool(self.db_path)
        
        # 初始化UI
        self.init_ui()
        
        # 初始化数据
        self.load_categories()
        self.load_images_async()
        
        # 更新最后登录时间
        self.user_manager.update_last_login(username)
        
        # 自动备份定时器
        self.auto_backup_timer = QTimer(self)
        self.auto_backup_timer.timeout.connect(self.auto_backup)
        self.auto_backup_interval = 3600000  # 1小时
        self.auto_backup_timer.start(self.auto_backup_interval)

        # 添加状态栏
        self.statusBar().showMessage(f"{ProjectInfo.NAME} v{ProjectInfo.VERSION} - 就绪")
        self.status_message_timer = QTimer(self)
        self.status_message_timer.setSingleShot(True)
        self.status_message_timer.timeout.connect(lambda: self.statusBar().showMessage("就绪"))
        
        # 进度对话框
        self.progress_dialog = None
    
    def init_ui(self):
        self.setWindowTitle(f"{ProjectInfo.get_version_string()} - 用户: {self.username}")
        self.resize(1200, 800)
        
        # 设置图标
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        # 创建菜单栏
        self.create_menus()
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧图片列表区域（包含分页控件）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置左侧面板最小宽度
        left_widget.setMinimumWidth(300)
    
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(100, 100))
        self.image_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_list.setMovement(QListWidget.Movement.Static)
        self.image_list.setSpacing(10)
        self.image_list.itemClicked.connect(self.on_image_selected)
        self.image_list.itemDoubleClicked.connect(self.on_image_double_clicked)
    
        # 设置列表部件的样式，确保背景色正确
        self.image_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QListWidget::item {
                background-color: white;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #e6f3ff;
            }
            QListWidget::item:selected {
                background-color: #cce8ff;
                color: black;
            }
        """)
        
        # 分页控件
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 5, 0, 5)
        
        self.prev_btn = QPushButton("◀ 上一页")
        self.prev_btn.clicked.connect(self.go_to_prev_page)
        self.prev_btn.setEnabled(False)
        
        self.page_label = QLabel("第 1 / 1 页")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.next_btn = QPushButton("下一页 ▶")
        self.next_btn.clicked.connect(self.go_to_next_page)
        self.next_btn.setEnabled(False)
        
        self.page_jump_edit = QLineEdit()
        self.page_jump_edit.setPlaceholderText("页码")
        self.page_jump_edit.setMaximumWidth(60)
        self.page_jump_edit.returnPressed.connect(self.jump_to_page)
        
        self.go_btn = QPushButton("跳转")
        self.go_btn.clicked.connect(self.jump_to_page)
        
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addWidget(self.page_jump_edit)
        pagination_layout.addWidget(self.go_btn)
        pagination_layout.addStretch()
        
        left_layout.addWidget(self.image_list)
        left_layout.addWidget(pagination_widget)
    
        # 在初始化时显示一个加载提示
        loading_item = QListWidgetItem("正在加载图片列表...")
        loading_item.setFlags(loading_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_list.addItem(loading_item)

        # 右侧详细信息面板 - 使用垂直布局，设置拉伸因子
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(10)
        
        # 图片显示区域 - 设置拉伸因子为1，使其占据所有可用空间
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 设置背景色和样式
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: #666;
                font-size: 14px;
            }
        """)
        self.image_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_label.mousePressEvent = self.on_image_clicked
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_image_context_menu)
        # 设置默认文本
        self.image_label.setText("暂无图片\n\n点击此处粘贴图片 (Ctrl+V)")
    
        # 添加到布局，设置拉伸因子为1
        right_layout.addWidget(self.image_label, 1)

        # 信息表单 - 固定高度区域
        form_group = QGroupBox("图片信息")
        form_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_layout = QFormLayout(form_group)
        
        self.name_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.tags_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
        form_layout.addRow("名称:", self.name_edit)
        form_layout.addRow("分类:", self.category_combo)
        form_layout.addRow("标签:", self.tags_edit)
        form_layout.addRow("描述:", self.description_edit)
        
        right_layout.addWidget(form_group, 0)  # 拉伸因子为0，固定高度

        # 操作按钮区域 - 固定高度
        button_widget = QWidget()
        button_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
    
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_image_info)
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_image)
        self.paste_button = QPushButton("粘贴图片 (Ctrl+V)")
        self.paste_button.clicked.connect(self.paste_image_from_clipboard)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.paste_button)
        button_layout.addStretch()
    
        right_layout.addWidget(button_widget, 0)  # 拉伸因子为0，固定高度

        # 搜索框区域 - 固定高度
        search_widget = QWidget()
        search_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
    
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索图片...")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self.search_images)
        
        clear_button = QPushButton("清除")
        clear_button.clicked.connect(self.clear_search)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
    
        right_layout.addWidget(search_widget, 0)  # 拉伸因子为0，固定高度
        
        # 添加一个伸缩因子在底部，确保所有内容靠上对齐
        right_layout.addStretch(0)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(QWidget())
        splitter.addWidget(right_widget)
    
        # 读取保存的分割器大小设置
        saved_sizes = self.settings.value("splitter_sizes")
        if saved_sizes:
            # 确保 saved_sizes 是整数列表
            if isinstance(saved_sizes, list):
                try:
                    # 将列表中的所有元素转换为整数
                    sizes = [int(x) for x in saved_sizes]
                    splitter.setSizes(sizes)
                except (ValueError, TypeError):
                    # 转换失败时使用默认比例
                    total_width = self.width()
                    left_width = int(total_width * 0.3)
                    middle_width = int(total_width * 0.05)
                    right_width = int(total_width * 0.65)
                    splitter.setSizes([left_width, middle_width, right_width])
            else:
                # 如果 saved_sizes 不是列表，使用默认比例
                total_width = self.width()
                left_width = int(total_width * 0.3)
                middle_width = int(total_width * 0.05)
                right_width = int(total_width * 0.65)
                splitter.setSizes([left_width, middle_width, right_width])
        else:
            # 否则按窗口大小比例分配
            total_width = self.width()
            left_width = int(total_width * 0.3)  # 左侧占30%
            middle_width = int(total_width * 0.05)  # 中间占5%
            right_width = int(total_width * 0.65)  # 右侧占65%
            splitter.setSizes([left_width, middle_width, right_width])
        
        # 连接分割器大小变化信号，保存设置
        splitter.splitterMoved.connect(self.save_splitter_sizes)
            
        main_layout.addWidget(splitter)
        
        # 添加快捷键
        self.paste_shortcut = QAction(self)
        self.paste_shortcut.setShortcut(QKeySequence("Ctrl+V"))
        self.paste_shortcut.triggered.connect(self.paste_image_from_clipboard)
        self.addAction(self.paste_shortcut)

    def on_search_text_changed(self, text):
        """搜索文本变化时自动搜索（带延迟）"""
        # 可以添加延迟搜索，避免频繁查询
        pass

    def clear_search(self):
        """清除搜索"""
        self.search_edit.clear()
        self.current_query = None
        self.current_page = 1
        self.load_images_async()

    def get_thumbnail(self, image_path, size=100):
        """获取缩略图（使用缓存）"""
        cache_key = f"thumb_{image_path}_{size}"
        pixmap = QPixmapCache.find(cache_key)
        
        if not pixmap or pixmap.isNull():
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                QPixmapCache.insert(cache_key, pixmap)
        
        return pixmap

    def on_image_clicked(self, event):
        """处理图片点击事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.current_image_id:
            # 获取当前图片路径
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM images WHERE id=?", (self.current_image_id,))
            result = cursor.fetchone()
            
            if result and os.path.exists(result[0]):
                # 创建并显示图片查看器
                self.image_viewer = ImageViewerDialog(result[0], self, initial_size=(1200, 900))
                self.image_viewer.show()
        
        if hasattr(super(), 'mousePressEvent'):
            super().mousePressEvent(event)

    def on_image_double_clicked(self, item):
        """处理图片列表项双击事件"""
        img_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 获取图片路径
        conn = self.db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM images WHERE id=?", (img_id,))
        result = cursor.fetchone()
        
        if result and os.path.exists(result[0]):
            self.image_viewer = ImageViewerDialog(result[0], self, initial_size=(1200, 900))
            self.image_viewer.show()

    def show_image_context_menu(self, pos):
        """显示图片上下文菜单"""
        if not self.current_image_id:
            return
        
        menu = QMenu(self)
        
        view_action = QAction("查看大图", self)
        view_action.triggered.connect(lambda: self.open_image_viewer())
        menu.addAction(view_action)
        
        copy_path_action = QAction("复制图片路径", self)
        copy_path_action.triggered.connect(self.copy_image_path_to_clipboard)
        menu.addAction(copy_path_action)
        
        open_folder_action = QAction("在文件夹中显示", self)
        open_folder_action.triggered.connect(self.open_image_in_explorer)
        menu.addAction(open_folder_action)
        
        menu.exec_(self.image_label.mapToGlobal(pos))

    def open_image_viewer(self):
        """打开图片查看器"""
        if self.current_image_id:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM images WHERE id=?", (self.current_image_id,))
            result = cursor.fetchone()
            
            if result and os.path.exists(result[0]):
                self.image_viewer = ImageViewerDialog(result[0], self, initial_size=(1200, 900))
                self.image_viewer.show()

    def copy_image_path_to_clipboard(self):
        """复制图片路径到剪贴板"""
        if self.current_image_id:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM images WHERE id=?", (self.current_image_id,))
            result = cursor.fetchone()
            
            if result:
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(result[0])
                self.show_status_message("图片路径已复制到剪贴板")

    def open_image_in_explorer(self):
        """在资源管理器中打开图片所在文件夹"""
        if self.current_image_id:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM images WHERE id=?", (self.current_image_id,))
            result = cursor.fetchone()
            
            if result and os.path.exists(result[0]):
                import platform
                import subprocess
                
                file_path = result[0]
                folder_path = os.path.dirname(file_path)
                
                try:
                    if platform.system() == "Windows":
                        os.startfile(folder_path)
                    elif platform.system() == "Darwin":
                        subprocess.Popen(["open", folder_path])
                    else:
                        subprocess.Popen(["xdg-open", folder_path])
                except Exception as e:
                    self.show_status_message(f"无法打开文件夹: {str(e)}", 5000)

    def create_menus(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        backup_action = QAction("手动备份", self)
        backup_action.triggered.connect(self.manual_backup)
        file_menu.addAction(backup_action)
        
        restore_action = QAction("恢复数据库", self)
        restore_action.triggered.connect(self.show_restore_dialog)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        self.logout_action = QAction("切换用户", self)
        self.logout_action.triggered.connect(self.logout)
        file_menu.addAction(self.logout_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 用户菜单
        user_menu = menubar.addMenu("用户")
        
        add_user_action = QAction("添加用户", self)
        add_user_action.triggered.connect(self.show_add_user_dialog)
        user_menu.addAction(add_user_action)
        
        delete_user_action = QAction("删除用户", self)
        delete_user_action.triggered.connect(self.show_delete_user_dialog)
        user_menu.addAction(delete_user_action)
        
        rename_user_action = QAction("重命名当前用户", self)
        rename_user_action.triggered.connect(self.show_rename_user_dialog)
        user_menu.addAction(rename_user_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        
        backup_settings_action = QAction("备份设置", self)
        backup_settings_action.triggered.connect(self.show_backup_settings_dialog)
        settings_menu.addAction(backup_settings_action)
    
        # 添加页面设置菜单项
        page_settings_action = QAction("页面设置", self)
        page_settings_action.triggered.connect(self.show_page_settings_dialog)
        settings_menu.addAction(page_settings_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(check_update_action)

    def show_page_settings_dialog(self):
        """显示页面设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("页面设置")
        dialog.resize(300, 150)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # 每页显示数量输入框
        page_size_spin = QSpinBox()
        page_size_spin.setRange(10, 1000)
        page_size_spin.setValue(self.PAGE_SIZE)
        page_size_spin.setSuffix(" 张")
        page_size_spin.setToolTip("设置每页显示的图片数量（10-1000张）")
        
        form_layout.addRow("每页显示数量:", page_size_spin)
        
        # 提示标签
        hint_label = QLabel("提示: 数量过大会影响加载速度")
        hint_label.setStyleSheet("color: #666; font-size: 10px;")
        
        layout.addLayout(form_layout)
        layout.addWidget(hint_label)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_page_size = page_size_spin.value()
            if new_page_size != self.PAGE_SIZE:
                self.PAGE_SIZE = new_page_size
                
                # 保存设置
                self.settings.setValue("page_size", self.PAGE_SIZE)
                
                # 重置当前页到第一页
                self.current_page = 1
                
                # 重新加载图片
                self.load_images_async()
                
                self.show_status_message(f"每页显示数量已设置为 {self.PAGE_SIZE} 张")


    def load_categories(self):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM images WHERE category IS NOT NULL AND category != '' ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        self.category_combo.clear()
        self.category_combo.addItem("")
        self.category_combo.addItems(categories)
    
    def load_images_async(self, query=None):
        """异步加载图片列表（分页）"""
        # 保存当前查询条件
        if query is not None:
            self.current_query = query
        
        # 禁用更新以提高性能
        self.image_list.setUpdatesEnabled(False)
        self.image_list.clear()
        
        def load():
            try:
                conn = self.db_pool.get_connection()
                cursor = conn.cursor()
                
                # 先查询总记录数
                if self.current_query:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM images i
                        JOIN images_fts f ON i.id = f.rowid
                        WHERE images_fts MATCH ?
                    """, (self.current_query,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM images")
                
                self.total_images = cursor.fetchone()[0]
                self.total_pages = max(1, (self.total_images + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
                
                # 确保当前页码有效
                if self.current_page > self.total_pages:
                    self.current_page = self.total_pages
                
                # 计算偏移量
                offset = (self.current_page - 1) * self.PAGE_SIZE
            
                # 如果没有图片，显示提示信息
                if self.total_images == 0:
                    self.image_list.setUpdatesEnabled(False)
                    self.image_list.clear()
                    empty_item = QListWidgetItem("暂无图片\n\n点击右侧的「粘贴图片 (Ctrl+V)」按钮或按 Ctrl+V 添加图片")
                    empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    empty_item.setSizeHint(QSize(200, 100))
                    self.image_list.addItem(empty_item)
                    self.image_list.setUpdatesEnabled(True)
                    
                    # 更新分页控件状态
                    self.update_pagination_controls()
                    
                    # 更新状态栏
                    self.show_status_message("暂无图片，请添加图片")
                    return
                
                # 查询当前页的数据
                if self.current_query:
                    cursor.execute("""
                        SELECT i.id, i.name, i.file_path 
                        FROM images i
                        JOIN images_fts f ON i.id = f.rowid
                        WHERE images_fts MATCH ?
                        ORDER BY i.name
                        LIMIT ? OFFSET ?
                    """, (self.current_query, self.PAGE_SIZE, offset))
                else:
                    cursor.execute("""
                        SELECT id, name, file_path 
                        FROM images 
                        ORDER BY name
                        LIMIT ? OFFSET ?
                    """, (self.PAGE_SIZE, offset))
                
                images = cursor.fetchall()
                
                # 分批添加图片项
                for i, (img_id, img_name, img_path) in enumerate(images):
                    if i % 10 == 0:
                        QApplication.processEvents()
                    
                    item = QListWidgetItem(img_name)
                    item.setData(Qt.ItemDataRole.UserRole, img_id)
                    
                    # 使用缓存缩略图
                    if os.path.exists(img_path):
                        pixmap = self.get_thumbnail(img_path)
                        if pixmap and not pixmap.isNull():
                            item.setIcon(QIcon(pixmap))
                    
                    self.image_list.addItem(item)
                
                # 更新分页控件状态
                self.update_pagination_controls()
                
                # 更新状态栏
                start_count = offset + 1 if self.total_images > 0 else 0
                end_count = min(offset + len(images), self.total_images)
                self.show_status_message(
                    f"第 {start_count}-{end_count} 张 / 共 {self.total_images} 张图片 "
                    f"(第 {self.current_page}/{self.total_pages} 页) - 每页 {self.PAGE_SIZE} 张"
                )
                
            except Exception as e:
                self.show_status_message(f"加载图片失败: {str(e)}", 5000)
            finally:
                self.image_list.setUpdatesEnabled(True)
        
        QTimer.singleShot(10, load)
    
    def update_pagination_controls(self):
        """更新分页控件状态"""
        self.page_label.setText(f"第 {self.current_page} / {self.total_pages} 页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
    
    def go_to_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_images_async()
    
    def go_to_next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_images_async()
    
    def jump_to_page(self):
        """跳转到指定页"""
        try:
            page = int(self.page_jump_edit.text())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self.load_images_async()
            else:
                self.show_status_message(f"页码必须在 1-{self.total_pages} 之间")
        except ValueError:
            self.show_status_message("请输入有效的页码")
    
    def on_image_selected(self, item):
        img_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_image_id = img_id
        
        conn = self.db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, description, category, tags, file_path FROM images WHERE id=?", (img_id,))
        result = cursor.fetchone()
        
        if result:
            name, description, category, tags, file_path = result
            
            self.name_edit.setText(name)
            self.description_edit.setPlainText(description if description else "")
            self.tags_edit.setText(tags if tags else "")
            
            # 设置分类
            index = self.category_combo.findText(category if category else "")
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentIndex(0)
                if category:
                    self.category_combo.setItemText(0, category)
            
            # 异步加载大图
            self.load_image_async(file_path)
    
    def load_image_async(self, file_path):
        """异步加载大图"""
        # 停止之前的加载线程
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.stop()
            self.load_thread.wait(500)  # 等待最多500ms
        
        # 创建新的加载线程
        self.load_thread = ImageLoadThread(file_path, self.image_label.size())
        self.load_thread.image_loaded.connect(self.on_image_loaded)
        self.load_thread.start()
    
    def on_image_loaded(self, pixmap, file_path):
        """图片加载完成的回调"""
        if pixmap and not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("")  # 清空默认文本
        else:
            self.image_label.setText("无法加载图片")
    
    def save_image_info(self):
        if not self.current_image_id:
            self.show_status_message("请先选择一张图片")
            return
        
        name = self.name_edit.text().strip()
        if not name:
            self.show_status_message("图片名称不能为空")
            return
        
        description = self.description_edit.toPlainText().strip()
        category = self.category_combo.currentText().strip()
        tags = self.tags_edit.text().strip()
        
        conn = self.db_pool.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE images 
            SET name=?, description=?, category=?, tags=?, update_time=CURRENT_TIMESTAMP 
            WHERE id=?
            ''', (name, description, category, tags, self.current_image_id))
            
            # 更新全文搜索索引
            cursor.execute("DELETE FROM images_fts WHERE rowid=?", (self.current_image_id,))
            cursor.execute('''
            INSERT INTO images_fts (rowid, name, description, category, tags) 
            VALUES (?, ?, ?, ?, ?)
            ''', (self.current_image_id, name, description, category, tags))
            
            conn.commit()
            
            # 更新列表显示
            self.load_images_async()
            self.load_categories()
            
            self.show_status_message("图片信息已保存")
        except Exception as e:
            conn.rollback()
            self.show_status_message(f"错误: 保存失败: {str(e)}", 5000)
    
    def delete_image(self):
        if not self.current_image_id:
            self.show_status_message("请先选择一张图片")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            "确定要删除这张图片吗?图片文件也将被删除!", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT file_path FROM images WHERE id=?", (self.current_image_id,))
                result = cursor.fetchone()
                if not result:
                    self.show_status_message("图片不存在")
                    return
                
                file_path = result[0]
                
                cursor.execute("DELETE FROM images WHERE id=?", (self.current_image_id,))
                cursor.execute("DELETE FROM images_fts WHERE rowid=?", (self.current_image_id,))
                conn.commit()
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 清除缓存
                QPixmapCache.remove(f"thumb_{file_path}_100")
                
                # 重新计算总页数
                if self.current_query:
                    cursor.execute("SELECT COUNT(*) FROM images i JOIN images_fts f ON i.id = f.rowid WHERE images_fts MATCH ?", (self.current_query,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM images")
                
                self.total_images = cursor.fetchone()[0]
                self.total_pages = max(1, (self.total_images + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
                
                # 如果当前页没有数据了，切换到上一页
                if self.current_page > self.total_pages and self.current_page > 1:
                    self.current_page = self.total_pages
                
                self.current_image_id = None
                self.name_edit.clear()
                self.description_edit.clear()
                self.tags_edit.clear()
                self.category_combo.setCurrentIndex(0)
                self.image_label.clear()
                self.image_label.setText("暂无图片\n\n点击此处粘贴图片 (Ctrl+V)")
                
                self.load_images_async()
                self.load_categories()
                
                self.show_status_message("图片已删除")
            except Exception as e:
                conn.rollback()
                self.show_status_message(f"删除失败: {str(e)}", 5000)
    
    def paste_image_from_clipboard(self):
        """粘贴图片（完全异步处理，不阻塞UI）"""
        # 先检查剪贴板内容
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            # 创建进度对话框
            self.progress_dialog = QProgressDialog("正在处理图片...", None, 0, 0, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.show()
            
            # 立即返回，让UI保持响应
            QTimer.singleShot(10, self._process_clipboard_image)
            
        elif mime_data.hasUrls():
            # 处理文件拖拽
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        self.progress_dialog = QProgressDialog("正在处理图片...", None, 0, 0, self)
                        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
                        self.progress_dialog.setCancelButton(None)
                        self.progress_dialog.show()
                        
                        QTimer.singleShot(10, lambda: self._process_local_image(file_path))
                    break
        else:
            self.show_status_message("剪贴板中没有可用的图片")
    
    def _process_clipboard_image(self):
        """异步处理剪贴板图片"""
        # 直接获取剪贴板图片（这个操作很快，不会阻塞）
        clipboard = QGuiApplication.clipboard()
        image = clipboard.image()
        
        if image and not image.isNull():
            # 启动保存线程
            self.save_thread = ImageSaveThread(self.db_pool, self.save_clipboard_image_sync, image)
            self.save_thread.finished.connect(self.on_image_save_finished)
            self.save_thread.start()
        else:
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            self.show_status_message("无法获取剪贴板图片")
    
    def _process_local_image(self, file_path):
        """异步处理本地图片"""
        self.save_thread = ImageSaveThread(self.db_pool, self.save_local_image_sync, file_path)
        self.save_thread.finished.connect(self.on_image_save_finished)
        self.save_thread.start()
    
    def on_image_save_finished(self, success, result):
        """图片保存完成后的处理"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if success:
            # 重新计算总页数并跳转到最后一页
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM images")
            self.total_images = cursor.fetchone()[0]
            self.total_pages = max(1, (self.total_images + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            self.current_page = self.total_pages  # 跳转到最后一页
            
            # 使用QTimer延迟刷新，避免阻塞
            QTimer.singleShot(100, lambda: self._refresh_after_save())
            self.show_status_message("图片已保存")
        else:
            self.show_status_message(f"保存失败: {result}", 5000)
    
    def _refresh_after_save(self):
        """保存后刷新界面"""
        self.load_images_async()
        self.load_categories()
    
    def save_clipboard_image_sync(self, db_pool, image):
        """同步保存剪贴板图片"""
        file_path = self.get_storage_path()
        
        if not image.save(file_path, "PNG"):
            return False
        
        # 获取数据库连接
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM images WHERE file_path=?", (file_path,))
            if cursor.fetchone():
                return False
            
            name = f"图片_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor.execute('''
            INSERT INTO images (name, file_path) 
            VALUES (?, ?)
            ''', (name, file_path))
            
            img_id = cursor.lastrowid
            
            cursor.execute('''
            INSERT INTO images_fts (rowid, name) 
            VALUES (?, ?)
            ''', (img_id, name))
            
            conn.commit()
            
            # 预生成缩略图缓存
            self.get_thumbnail(file_path)
            
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            try:
                os.remove(file_path)
            except OSError:
                pass
            return False
    
    def save_local_image_sync(self, db_pool, file_path):
        """同步保存本地图片"""
        new_file_path = self.get_storage_path(file_path)
        
        if os.path.exists(new_file_path):
            return False
        
        try:
            shutil.copy2(file_path, new_file_path)
            
            conn = db_pool.get_connection()
            cursor = conn.cursor()
            
            try:
                name = os.path.splitext(os.path.basename(file_path))[0]
                
                cursor.execute('''
                INSERT INTO images (name, file_path) 
                VALUES (?, ?)
                ''', (name, new_file_path))
                
                img_id = cursor.lastrowid
                
                cursor.execute('''
                INSERT INTO images_fts (rowid, name) 
                VALUES (?, ?)
                ''', (img_id, name))
                
                conn.commit()
                
                # 预生成缩略图缓存
                self.get_thumbnail(new_file_path)
                
                return True
                
            except sqlite3.Error as e:
                conn.rollback()
                try:
                    os.remove(new_file_path)
                except OSError:
                    pass
                return False
                
        except Exception as e:
            return False
    
    def search_images(self):
        query = self.search_edit.text().strip()
        self.current_query = query if query else None
        self.current_page = 1  # 搜索时重置到第一页
        self.load_images_async()
    
    def auto_backup(self):
        try:
            self.backup_manager.create_backup(self.db_path, "auto")
        except Exception as e:
            print(f"自动备份失败: {e}")
    
    def manual_backup(self):
        try:
            backup_path = self.backup_manager.create_backup(self.db_path, "manual")
            self.show_status_message(f"数据库已备份到: {os.path.basename(backup_path)}")
        except Exception as e:
            self.show_status_message(f"备份失败: {str(e)}", 5000)
    
    def show_restore_dialog(self):
        dialog = RestoreDatabaseDialog(self.backup_manager, self.db_path, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 恢复完成后需要重新初始化
            self.db_pool.close_all()
            # 重新初始化数据库连接池
            self.db_pool = DatabasePool(self.db_path)
            
            self.current_image_id = None
            self.name_edit.clear()
            self.description_edit.clear()
            self.tags_edit.clear()
            self.category_combo.setCurrentIndex(0)
            self.image_label.clear()
            self.image_label.setText("暂无图片\n\n点击此处粘贴图片 (Ctrl+V)")
            
            self.current_page = 1
            self.load_images_async()
            self.load_categories()
            
            self.show_status_message("数据库已恢复，界面已刷新")
    
    def show_add_user_dialog(self):
        username, ok = QInputDialog.getText(
            self, "添加用户", "请输入新用户名:", 
            QLineEdit.EchoMode.Normal, "")
        
        if ok and username:
            if self.user_manager.add_user(username):
                self.show_status_message(f"用户 {username} 已添加")
            else:
                self.show_status_message("用户名已存在")
    
    def show_delete_user_dialog(self):
        users = self.user_manager.get_all_users()
        usernames = [user[1] for user in users if user[1] != self.username]
        
        if not usernames:
            self.show_status_message("没有其他用户可删除")
            return
        
        username, ok = QInputDialog.getItem(
            self, "删除用户", "选择要删除的用户:", 
            usernames, 0, False)
        
        if ok and username:
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除用户 {username} 吗?所有数据将丢失!", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.user_manager.delete_user(username)
                self.show_status_message(f"用户 {username} 已删除")
    
    def show_rename_user_dialog(self):
        new_name, ok = QInputDialog.getText(
            self, "重命名用户", "请输入新用户名:", 
            QLineEdit.EchoMode.Normal, self.username)
        
        if ok and new_name and new_name != self.username:
            if self.user_manager.update_username(self.username, new_name):
                self.username = new_name
                self.setWindowTitle(f"{ProjectInfo.get_version_string()} - 用户: {self.username}")
                self.show_status_message(f"用户名已更改为 {new_name}")
            else:
                self.show_status_message("用户名已存在或无效")
    
    def show_backup_settings_dialog(self):
        max_backups, ok = QInputDialog.getInt(
            self, "备份设置", "最大备份数量:", 
            self.backup_manager.max_backups, 1, 100, 1)
        
        if ok:
            self.backup_manager.max_backups = max_backups
            self.show_status_message(f"最大备份数量已设置为 {max_backups}")

    def get_storage_path(self, original_path=None):
        """生成分目录存储路径"""
        storage_root = os.path.join(os.path.dirname(self.db_path), "images")
        user_dir = os.path.join(storage_root, f"user_{self.username}")
        
        now = datetime.now()
        date_dir = os.path.join(user_dir, 
                            f"{now.year}", 
                            f"{now.month:02d}", 
                            f"{now.day:02d}")
        
        os.makedirs(date_dir, exist_ok=True)
        
        if original_path:
            _, ext = os.path.splitext(original_path)
            ext = ext.lower()
            
            try:
                with open(original_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            except:
                file_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()
            
            return os.path.join(date_dir, f"{file_hash}{ext}")
        else:
            return os.path.join(date_dir, f"clip_{now.strftime('%Y%m%d_%H%M%S')}.png")

    def logout(self):
        """注销当前用户"""
        self.db_pool.close_all()
        self.close()
        self.logout_requested.emit()

    def show_status_message(self, message, timeout=3000):
        """在状态栏显示消息"""
        self.statusBar().showMessage(message)
        if timeout > 0:
            self.status_message_timer.start(timeout)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有线程
        if self.save_thread and self.save_thread.isRunning():
            self.save_thread.quit()
            self.save_thread.wait(1000)
        
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.stop()
            self.load_thread.wait(1000)
        
        # 关闭所有数据库连接
        self.db_pool.close_all()
    
        # 确保分割器大小被保存
        self.save_splitter_sizes()

        event.accept()

    def show_about_dialog(self):
        """显示关于对话框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("关于")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(ProjectInfo.get_about_html())
        
        # 添加详细信息按钮
        details_button = msg_box.addButton("详细信息", QMessageBox.ButtonRole.ActionRole)
        ok_button = msg_box.addButton(QMessageBox.StandardButton.Ok)
        
        def on_button_clicked(button):
            if button == details_button:
                # 显示详细信息
                QMessageBox.information(
                    self, "详细信息", 
                    f"{ProjectInfo.get_full_info()}\n\n"
                    f"系统要求:\n"
                    f"{chr(10).join([f'  {k}: {v}' for k, v in ProjectInfo.get_system_requirements().items()])}"
                )
        
        msg_box.buttonClicked.connect(on_button_clicked)
        msg_box.exec()
        
    def check_for_updates(self):
        """检查更新（带进度提示）"""
        # 显示正在检查
        self.statusBar().showMessage("正在检查更新...")
        
        # 使用QTimer延迟执行，避免阻塞UI
        QTimer.singleShot(100, self._do_check_updates)

    def _do_check_updates(self):
        """实际执行检查更新"""
        try:
            # 创建一个简单的等待对话框
            from PySide6.QtWidgets import QProgressDialog
            
            progress = QProgressDialog("正在检查更新...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setCancelButton(None)
            progress.show()
            
            # 让UI有机会更新
            QApplication.processEvents()
            
            # 执行检查
            message = ProjectInfo.get_update_message()
            
            # 关闭进度对话框
            progress.close()
            
            # 显示结果
            QMessageBox.information(self, "检查更新", message)
            self.statusBar().showMessage(f"{ProjectInfo.NAME} v{ProjectInfo.VERSION} - 就绪")
            
        except Exception as e:
            if progress:
                progress.close()
            QMessageBox.warning(self, "检查更新", f"检查更新时出错: {str(e)}")
            self.statusBar().showMessage(f"{ProjectInfo.NAME} v{ProjectInfo.VERSION} - 就绪")

    def save_splitter_sizes(self):
        """保存分割器大小设置"""
        splitter = self.findChild(QSplitter)
        if splitter:
            # 获取当前分割器大小
            sizes = splitter.sizes()
            # 确保所有值都是整数
            sizes = [int(x) for x in sizes]
            # 保存到设置中
            self.settings.setValue("splitter_sizes", sizes)

# 数据库恢复对话框
class RestoreDatabaseDialog(QDialog):
    def __init__(self, backup_manager, db_path, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.db_path = db_path
        self.selected_backup = None
        
        self.setWindowTitle("恢复数据库")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 筛选区域
        filter_group = QGroupBox("筛选条件")
        filter_layout = QHBoxLayout()
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("所有类型", "")
        self.type_filter.addItem("自动备份", "auto")
        self.type_filter.addItem("手动备份", "manual")
        self.type_filter.addItem("回滚备份", "rollback")
        self.type_filter.currentIndexChanged.connect(self.update_backup_list)
        
        self.date_from = QDateTimeEdit()
        self.date_from.setDateTime(QDateTime.currentDateTime().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.dateTimeChanged.connect(self.update_backup_list)
        
        self.date_to = QDateTimeEdit()
        self.date_to.setDateTime(QDateTime.currentDateTime())
        self.date_to.setCalendarPopup(True)
        self.date_to.dateTimeChanged.connect(self.update_backup_list)
        
        filter_layout.addWidget(QLabel("备份类型:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("时间范围:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("至"))
        filter_layout.addWidget(self.date_to)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 备份列表表格
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(5)
        self.backup_table.setHorizontalHeaderLabels(["时间", "类型", "大小", "操作", ""])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.backup_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.backup_table)
        
        # 详细信息区域
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)
        
        # 按钮区域
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.restore_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.restore_button.setText("恢复")
        self.restore_button.setEnabled(False)
        
        layout.addWidget(button_box)
        
        # 初始加载备份列表
        self.update_backup_list()
    
    def update_backup_list(self):
        backups = self.backup_manager.get_all_backups()
        
        # 应用筛选
        filter_type = self.type_filter.currentData()
        date_from = self.date_from.dateTime().toPython()
        date_to = self.date_to.dateTime().toPython()
        
        filtered_backups = []
        for backup in backups:
            if filter_type and backup['type'] != filter_type:
                continue
            if backup['time'] < date_from or backup['time'] > date_to:
                continue
            filtered_backups.append(backup)
        
        # 更新表格
        self.backup_table.setRowCount(len(filtered_backups))
        
        for row, backup in enumerate(filtered_backups):
            # 时间
            time_item = QTableWidgetItem(backup['time'].strftime("%Y-%m-%d %H:%M:%S"))
            time_item.setData(Qt.ItemDataRole.UserRole, backup['filepath'])
            
            # 类型
            type_text = {
                'auto': '自动',
                'manual': '手动',
                'rollback': '回滚'
            }.get(backup['type'], backup['type'])
            type_item = QTableWidgetItem(type_text)
            
            # 大小
            size_mb = backup['size'] / (1024 * 1024)
            size_item = QTableWidgetItem(f"{size_mb:.2f} MB")
            
            # 预览按钮
            preview_btn = QPushButton("预览")
            preview_btn.clicked.connect(lambda _, b=backup: self.show_backup_details(b))
            
            # 恢复按钮
            restore_btn = QPushButton("恢复")
            restore_btn.clicked.connect(lambda _, b=backup: self.select_backup(b))
            
            self.backup_table.setItem(row, 0, time_item)
            self.backup_table.setItem(row, 1, type_item)
            self.backup_table.setItem(row, 2, size_item)
            self.backup_table.setCellWidget(row, 3, preview_btn)
            self.backup_table.setCellWidget(row, 4, restore_btn)
    
    def show_backup_details(self, backup):
        try:
            conn = sqlite3.connect(backup['filepath'])
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM images")
            image_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(create_time), MAX(create_time) FROM images")
            min_date, max_date = cursor.fetchone()
            
            cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            
            conn.close()
            
            details = (
                f"备份时间: {backup['time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"备份类型: {backup['type']}\n"
                f"图片数量: {image_count}\n"
                f"日期范围: {min_date} 至 {max_date}\n"
                f"数据库版本: {version}\n"
                f"文件大小: {backup['size'] / (1024 * 1024):.2f} MB"
            )
            
            self.details_label.setText(details)
            self.selected_backup = backup
            self.restore_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取备份信息: {str(e)}")
            self.details_label.setText("无法读取备份信息")
            self.selected_backup = None
            self.restore_button.setEnabled(False)
    
    def select_backup(self, backup):
        self.show_backup_details(backup)
    
    def accept(self):
        if not self.selected_backup:
            QMessageBox.warning(self, "警告", "请先选择一个备份")
            return
        
        reply = QMessageBox.question(
            self, "确认恢复", 
            f"确定要恢复数据库到 {self.selected_backup['time'].strftime('%Y-%m-%d %H:%M:%S')} 的状态吗?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                rollback_path = self.backup_manager.restore_backup(
                    self.selected_backup['filepath'], self.db_path)
                
                QMessageBox.information(
                    self, "成功", 
                    f"数据库已恢复，恢复前的状态已备份到:\n{rollback_path}")
                
                super().accept()
            except Exception as e:
                if hasattr(self.parent(), 'show_status_message'):
                    self.parent().show_status_message(f"恢复失败: {str(e)}", 5000)

# 图片查看器对话框类
class ImageViewerDialog(QDialog):
    def __init__(self, image_path, parent=None, initial_size=None):
        super().__init__(parent)
        self.image_path = image_path
        self.zoom_factor = 1.0
        self.pan_start_pos = None
        self.pan_offset = [0, 0]
        self.initial_size = initial_size
        self.init_ui()
        
        # 初始化时立即保存一次窗口状态
        self.save_window_state()
        
    def init_ui(self):
        self.setWindowTitle("图片查看器")
        
        # 读取保存的窗口大小设置
        settings = QSettings("ImageManager", "ImageViewer")
        
        saved_size = settings.value("window_size")
        saved_maximized = settings.value("window_maximized", False, type=bool)
        saved_position = settings.value("window_position")
        
        if self.initial_size:
            default_size = QSize(self.initial_size[0], self.initial_size[1])
        else:
            default_size = QSize(800, 600)
        
        if saved_position and not saved_maximized:
            try:
                self.move(saved_position)
            except:
                pass
        
        if saved_size and not saved_maximized:
            try:
                self.resize(saved_size)
            except:
                self.resize(default_size)
        else:
            self.resize(default_size)
        
        if saved_maximized:
            self.showMaximized()
        
        # 主布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
    
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
    
        # 加载图片
        self.load_image()
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("放大 (+)")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn = QPushButton("缩小 (-)")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_zoom_btn = QPushButton("重置缩放")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        self.fit_window_btn = QPushButton("适应窗口")
        self.fit_window_btn.clicked.connect(self.fit_to_window)
        
        self.original_size_btn = QPushButton("原始大小")
        self.original_size_btn.clicked.connect(self.show_original_size)
        
        self.copy_path_btn = QPushButton("复制路径")
        self.copy_path_btn.clicked.connect(self.copy_image_path)

        self.reset_window_btn = QPushButton("重置窗口")
        self.reset_window_btn.clicked.connect(self.reset_window_size)

        control_layout.addWidget(self.zoom_in_btn)
        control_layout.addWidget(self.zoom_out_btn)
        control_layout.addWidget(self.reset_zoom_btn)
        control_layout.addWidget(self.fit_window_btn)
        control_layout.addWidget(self.original_size_btn)
        control_layout.addWidget(self.copy_path_btn)
        control_layout.addWidget(self.reset_window_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 状态标签
        layout.addWidget(self.status_label)
        
        self.image_label.setMouseTracking(True)
        
        # 添加快捷键
        self.zoom_in_shortcut = QAction(self)
        self.zoom_in_shortcut.setShortcut(QKeySequence("Ctrl++"))
        self.zoom_in_shortcut.triggered.connect(self.zoom_in)
        self.addAction(self.zoom_in_shortcut)
        
        self.zoom_out_shortcut = QAction(self)
        self.zoom_out_shortcut.setShortcut(QKeySequence("Ctrl+-"))
        self.zoom_out_shortcut.triggered.connect(self.zoom_out)
        self.addAction(self.zoom_out_shortcut)
        
        self.reset_zoom_shortcut = QAction(self)
        self.reset_zoom_shortcut.setShortcut(QKeySequence("Ctrl+0"))
        self.reset_zoom_shortcut.triggered.connect(self.reset_zoom)
        self.addAction(self.reset_zoom_shortcut)
        
        # 替换wheelEvent
        self.scroll_area.wheelEvent = self.wheel_event
        
        self.reset_zoom()

    def reset_window_size(self):
        """重置窗口大小为默认大小"""
        settings = QSettings("ImageManager", "ImageViewer")
        settings.remove("window_size")
        settings.remove("window_maximized")
        settings.remove("window_position")
        
        if self.isMaximized():
            self.showNormal()
        
        if self.initial_size:
            self.resize(self.initial_size[0], self.initial_size[1])
        else:
            self.resize(800, 600)
        
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        self.show_status_message("窗口大小已重置")

    def save_window_state(self):
        """统一保存窗口状态"""
        settings = QSettings("ImageManager", "ImageViewer")
        
        settings.setValue("window_maximized", self.isMaximized())
        
        if not self.isMaximized():
            settings.setValue("window_size", self.size())
            settings.setValue("window_position", self.pos())

    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == QEvent.Type.WindowStateChange:
            self.save_window_state()
        
        super().changeEvent(event)

    def moveEvent(self, event):
        """处理窗口移动事件"""
        if not self.isMaximized():
            self.save_window_state()
        
        super().moveEvent(event)

    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        if not self.isMaximized():
            self.save_window_state()
        
        super().resizeEvent(event)

    def closeEvent(self, event):
        """保存窗口大小到设置"""
        self.save_window_state()
        super().closeEvent(event)

    def load_image(self):
        """加载图片"""
        if os.path.exists(self.image_path):
            self.original_pixmap = QPixmap(self.image_path)
            if not self.original_pixmap.isNull():
                self.display_pixmap = self.original_pixmap.copy()
                self.image_label.setPixmap(self.display_pixmap)
                self.original_size = self.original_pixmap.size()
            else:
                self.image_label.setText("无法加载图片")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("无法加载图片")
        else:
            self.image_label.setText("图片文件不存在")
            if hasattr(self, 'status_label'):
                self.status_label.setText("图片文件不存在")

    def update_image(self):
        """更新显示的图片"""
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            new_width = int(self.original_size.width() * self.zoom_factor)
            new_height = int(self.original_size.height() * self.zoom_factor)
            
            scaled_pixmap = self.original_pixmap.scaled(
                new_width, new_height, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.display_pixmap = scaled_pixmap
            self.image_label.setPixmap(self.display_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            
            self.update_status()
    
    def zoom_in(self):
        """放大图片"""
        self.zoom_factor *= 1.2
        self.update_image()
    
    def zoom_out(self):
        """缩小图片"""
        self.zoom_factor /= 1.2
        if self.zoom_factor < 0.1:
            self.zoom_factor = 0.1
        self.update_image()
    
    def reset_zoom(self):
        """重置缩放"""
        self.zoom_factor = 1.0
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            self.update_image()

    def fit_to_window(self):
        """适应窗口大小"""
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            viewport_size = self.scroll_area.viewport().size()
            pixmap_size = self.original_pixmap.size()
            
            width_ratio = viewport_size.width() / pixmap_size.width()
            height_ratio = viewport_size.height() / pixmap_size.height()
            self.zoom_factor = min(width_ratio, height_ratio) * 0.9
            
            self.update_image()
    
    def show_original_size(self):
        """显示原始大小"""
        self.zoom_factor = 1.0
        self.update_image()
    
    def copy_image_path(self):
        """复制图片路径到剪贴板"""
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.image_path)
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"已复制路径: {self.image_path}")
        
        QTimer.singleShot(3000, self.update_status)
    
    def show_status_message(self, message):
        """显示状态消息"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
    
    def update_status(self):
        """更新状态信息"""
        if hasattr(self, 'status_label'):
            if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
                info = f"路径: {self.image_path} | "
                info += f"原始尺寸: {self.original_size.width()}×{self.original_size.height()} | "
                info += f"当前缩放: {self.zoom_factor:.2f}x | "
                info += f"当前尺寸: {int(self.original_size.width() * self.zoom_factor)}×{int(self.original_size.height() * self.zoom_factor)}"
                self.status_label.setText(info)
            else:
                self.status_label.setText(f"路径: {self.image_path}")

    def wheel_event(self, event):
        """处理鼠标滚轮事件"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super(QScrollArea, self.scroll_area).wheelEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pan_start_pos = event.pos()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽图片"""
        if self.pan_start_pos is not None:
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()
            
            h_scroll = self.scroll_area.horizontalScrollBar()
            v_scroll = self.scroll_area.verticalScrollBar()
            h_scroll.setValue(h_scroll.value() - delta.x())
            v_scroll.setValue(v_scroll.value() - delta.y())
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pan_start_pos = None
            event.accept()
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key.Key_0:
            self.reset_zoom()
        elif event.key() == Qt.Key.Key_F:
            self.fit_to_window()
        elif event.key() == Qt.Key.Key_O:
            self.show_original_size()
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.copy_image_path()
        else:
            super().keyPressEvent(event)

# 用户选择对话框
class UserSelectionDialog(QDialog):
    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        
        self.setWindowTitle(f"{ProjectInfo.NAME} v{ProjectInfo.VERSION} - 选择用户")
        self.resize(400, 300)
        
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
                    
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        self.user_list = QListWidget()
        self.update_user_list()
        self.user_list.itemDoubleClicked.connect(self.accept)
        
        layout.addWidget(QLabel("请选择用户:"))
        layout.addWidget(self.user_list)
        
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self.accept)
        
        self.add_user_button = QPushButton("添加用户")
        self.add_user_button.clicked.connect(self.add_user)
        
        self.delete_user_button = QPushButton("删除用户")
        self.delete_user_button.clicked.connect(self.delete_user)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.add_user_button)
        button_layout.addWidget(self.delete_user_button)
        
        layout.addLayout(button_layout)
        
        self.status_message_timer = QTimer(self)
        self.status_message_timer.setSingleShot(True)
        self.status_message_timer.timeout.connect(lambda: self.status_bar.showMessage("就绪"))

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.reject()

    def show_status_message(self, message, timeout=3000):
        self.status_bar.showMessage(f"{ProjectInfo.NAME} v{ProjectInfo.VERSION} - {message}")
        if timeout > 0:
            self.status_message_timer.start(timeout)
            
    def update_user_list(self):
        self.user_list.clear()
        users = self.user_manager.get_all_users()
        for user in users:
            item = QListWidgetItem(user[1])
            item.setData(Qt.ItemDataRole.UserRole, user[1])
            last_login = user[2] if user[2] else "从未登录"
            item.setToolTip(f"最后登录: {last_login}")
            self.user_list.addItem(item)
    
    def add_user(self):
        username, ok = QInputDialog.getText(
            self, "添加用户", "请输入新用户名:", 
            QLineEdit.EchoMode.Normal, "")
        
        if ok and username:
            if self.user_manager.add_user(username):
                self.update_user_list()
                self.show_status_message(f"用户 {username} 已添加")
            else:
                self.show_status_message("用户名已存在")
    
    def delete_user(self):
        current_item = self.user_list.currentItem()
        if not current_item:
            self.show_status_message("请先选择一个用户")
            return
        
        username = current_item.data(Qt.ItemDataRole.UserRole)
        if username:
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除用户 {username} 吗?所有数据将丢失!", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.user_manager.delete_user(username)
                self.update_user_list()
                self.show_status_message(f"用户 {username} 已删除")
    
    def get_selected_user(self):
        current_item = self.user_list.currentItem()
        return current_item.data(Qt.ItemDataRole.UserRole) if current_item else None
    
    def accept(self):
        if not self.get_selected_user():
            self.show_status_message("请先选择一个用户")
            return
        super().accept()

# 主程序
class ImageManagerApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(ProjectInfo.NAME)
        self.setApplicationVersion(ProjectInfo.VERSION)
        
        # 创建必要的目录
        ProjectInfo.create_directories()
        
        app_dir = ProjectInfo.get_app_dir()
        self.user_manager = UserManager(app_dir)
        self.current_window = None
        self.user_dialog = None
        
        # 打印项目信息（调试用）
        ProjectInfo.print_info()
        
        self.show_user_dialog()
        
    def show_user_dialog(self):
        self.user_dialog = UserSelectionDialog(self.user_manager)
        self.user_dialog.finished.connect(self.on_user_dialog_finished)
        self.user_dialog.show()
        
    def on_user_dialog_finished(self, result):
        if result == QDialog.DialogCode.Accepted:
            username = self.user_dialog.get_selected_user()
            if username:
                self.show_main_window(username)
            else:
                self.quit()
        else:
            self.quit()

    def show_main_window(self, username):
        if self.current_window:
            self.current_window.close()
            
        self.current_window = ImageManagerWindow(self.user_manager, username)
        self.current_window.logout_requested.connect(self.on_logout_requested)
        self.current_window.show()
    
    def on_logout_requested(self):
        self.current_window = None
        self.show_user_dialog()
    

if __name__ == "__main__":
    app = ImageManagerApp(sys.argv)
    sys.exit(app.exec())