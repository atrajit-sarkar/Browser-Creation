import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QToolBar, QAction, QMenu, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon
from adblockparser import AdblockRules

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Atrajit Explorer')
        self.setGeometry(300, 150, 1200, 800)

        # Set the window icon
        self.setWindowIcon(QIcon('logo.png'))  # Update the path to your logo file

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://www.google.com'))

        # Enable plugins and full-screen support
        self.browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.browser.page().fullScreenRequested.connect(self.handle_fullscreen)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.go_button = QPushButton('Go')
        self.go_button.clicked.connect(self.navigate_to_url)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.browser.back)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.browser.reload)

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_bar)
        url_layout.addWidget(self.go_button)
        # layout.addWidget(self.back_button)
        # layout.addWidget(self.refresh_button)
        layout = QVBoxLayout()
        layout.addLayout(url_layout)  # Add the horizontal layout to the main vertical layout
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add navigation toolbar
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        navtb.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # Add full-screen toggle
        fullscreen_btn = QAction("Toggle Full Screen", self)
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        navtb.addAction(fullscreen_btn)

        # Add status indicators
        self.status_label = QLabel("Status: Normal")
        navtb.addWidget(self.status_label)

        # Add settings menu
        settings_menu = QMenu("Settings", self)
        private_mode_action = QAction("Toggle Private Browsing", self)
        private_mode_action.triggered.connect(self.toggle_private_browsing)
        settings_menu.addAction(private_mode_action)

        adblock_action = QAction("Toggle Ad Blocker", self)
        adblock_action.triggered.connect(self.toggle_adblock)
        settings_menu.addAction(adblock_action)

        https_only_action = QAction("Enable HTTPS-Only Mode", self)
        https_only_action.triggered.connect(self.enable_https_only)
        settings_menu.addAction(https_only_action)

        user_agent_action = QAction("Set Custom User Agent", self)
        user_agent_action.triggered.connect(self.set_custom_user_agent)
        settings_menu.addAction(user_agent_action)

        cookie_management_action = QAction("Manage Cookies", self)
        cookie_management_action.triggered.connect(self.manage_cookies)
        settings_menu.addAction(cookie_management_action)

        menu_bar = self.menuBar()
        menu_bar.addMenu(settings_menu)

        self.private_browsing_enabled = False
        self.adblock_enabled = False

        # Ensure YouTube videos play in high quality
        self.browser.page().loadFinished.connect(self.set_youtube_quality)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('https://'):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))

    def navigate_home(self):
        self.browser.setUrl(QUrl('https://www.google.com'))

    def handle_fullscreen(self, request):
        request.accept()
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def toggle_private_browsing(self):
        if self.private_browsing_enabled:
            profile = QWebEngineProfile.defaultProfile()
            self.status_label.setText("Status: Normal")
        else:
            profile = QWebEngineProfile()
            self.status_label.setText("Status: Private Browsing")
        page = QWebEnginePage(profile)
        self.browser.setPage(page)
        self.private_browsing_enabled = not self.private_browsing_enabled

    def toggle_adblock(self):
        if self.adblock_enabled:
            self.browser.page().profile().setRequestInterceptor(None)
            self.status_label.setText("Status: Ad Blocker Disabled")
        else:
            with open(r"D:\downloads\Python\Projects\Browser Creation\youtube_clear_view.txt",encoding='UTF-8') as f:  # Update the path to your easylist.txt file
                raw_rules = f.readlines()
            self.rules = AdblockRules(raw_rules)
            interceptor = WebEngineUrlRequestInterceptor(self.rules)
            self.browser.page().profile().setRequestInterceptor(interceptor)
            self.status_label.setText("Status: Ad Blocker Enabled")
        self.adblock_enabled = not self.adblock_enabled

    def enable_https_only(self):
        self.browser.urlChanged.connect(self.force_https)
        self.status_label.setText("Status: HTTPS-Only Mode Enabled")

    def force_https(self, url):
        if url.scheme() != 'https':
            secure_url = QUrl(url)
            secure_url.setScheme('https')
            self.browser.setUrl(secure_url)

    def set_custom_user_agent(self):
        user_agent = "Your Custom User Agent String"
        self.browser.page().profile().setHttpUserAgent(user_agent)
        self.status_label.setText("Status: Custom User Agent Set")

    def manage_cookies(self):
        cookie_store = self.browser.page().profile().cookieStore()
        cookie_store.deleteAllCookies()
        self.status_label.setText("Status: Cookies Cleared")

    def set_youtube_quality(self):
        script = """
        var player = document.getElementById('movie_player');
        if (player) {
            player.setPlaybackQualityRange('hd1080');
            player.setPlaybackQuality('hd1080');
        }
        """
        self.browser.page().runJavaScript(script)

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, rules):
        super().__init__()
        self.rules = rules

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if self.rules.should_block(url):
            info.block(True)

app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())
