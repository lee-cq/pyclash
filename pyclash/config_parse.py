#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config_parse.py
@Author     : LeeCQ
@Date-Time  : 2022/11/30 22:22

Clash 配置文件解析
"""
import logging
import os.path
import urllib.request

from yaml import safe_load, safe_dump

logger = logging.getLogger("pyclash.config.parse")


class Authentication(list):
    """
    认证信息
    """
    logger = logging.getLogger("pyclash.config.parse.authentication")

    def add_auth(self, username: str, password: str):
        """添加认证信息

        :return:
        """
        self.append(f'{username}:{password}')


class Dns(dict):
    """
    DNS 配置
    """
    logger = logging.getLogger("pyclash.config.parse.dns")
    _name_map = {

    }

    def __init__(self, config: dict = None):
        super().__init__(config or {})

        # self.enable = True
        # self.listen = '0.0.0.0:53'
        # self.default_nameserver = ['114.114.114.114', '8.8.8.8']
        # self.nameserver = []
        # self.fallback = []
        # self.fallback_filter = {'geoip': True, 'ipcidr': []}
        # self.enhanced_mode = 'redir-host'
        # self.fake_ip_range = '198.168.0.1/16'
        # self.fake_ip_filter = ['+.*clash.*']
        # self.use_local_resolver = True
        # self.ipv6 = False
        # self.listen_ipv6 = False
        # self.nameserver_policy = {}


class Proxy(dict):
    logger = logging.getLogger("pyclash.config.parse.proxy")

    def __init__(self, config: dict = None):
        super().__init__(config or {})
        # self.proxy_name = ''
        # self.type = ''
        # self.name = ''
        # self.server = ''
        # self.port = 0
        # self.password = ''
        # self.cipher = ''
        # self.udp = False
        # self.tfo = False
        # self.skip_cert_verify = False
        # self.sni = ''
        # self.alpn = []
        # self.early_data = False
        # self.verify_hostname = False
        # self.server_name = ''
        # self.path = ''


class ProxyGroup(dict):
    logger = logging.getLogger("pyclash.config.parse.proxy_group")

    def __init__(self, config: dict = None):
        super().__init__(config or {})
        # self.name = ''
        # self.type = ''
        # self.proxies = []
        # self.url = ''
        # self.interval = 0
        # self.path = ''
        # self.interface_name = ''
        # self.use = []


class ProxyProvider:
    """代理提供者"""
    logger = logging.getLogger("pyclash.config.parse.proxy_provider")

    def __init__(self, config: dict = None):
        super().__init__(config or {})
        # self.name = ''
        # self.type = ''
        # self.path = ''
        # self.url = ''
        # self.interval = 0
        # self.health_check = False
        # self.health_check_url = ''
        # self.health_check_interval = 0
        # self.proxies = []


class Tunnel(dict):
    logger = logging.getLogger("pyclash.config.parse.tunnel")

    def __init__(self, config: dict = None):
        super().__init__(config or {})
        self.enable = False
        self.tun_device = 'tun0'
        self.tun_device_ip = ''


class ConfigParse(dict):
    """配置文件解析

    Clash配置文件原文：https://github.com/Dreamacro/clash/wiki/Configuration#all-configuration-options

    """
    logger = logging.getLogger("pyclash.config.parse")

    _name_map = {
        'dns': Dns,
        'proxies': Proxy,
        'proxy-groups': ProxyGroup,
        'proxy-providers': ProxyProvider,
        'tunnel': Tunnel,
    }

    def __init__(self, config: dict = None):
        self.logger.debug("Input config: %s", config)
        super().__init__(config or {})
        self._parse()

    def _parse(self):
        _config = self.copy()
        for key, value in _config.items():
            logger.debug("Parse %s: (%s)%s", key, type(value), value)
            if key in self._name_map:
                if isinstance(value, list):
                    self[key] = [self._name_map[key](item) for item in value]
                elif isinstance(value, dict):
                    self[key] = self._name_map[key](value)

    @classmethod
    def from_uri(cls, uri: str):
        """从 URI 加载配置"""
        urllib.request.urlretrieve(uri, 'config.yaml')
        with open('config.yaml', 'r', encoding='utf8') as f:
            return cls(safe_load(f))

    @classmethod
    def from_yaml(cls, yaml_str: str):
        """从 YAML 加载配置"""
        cls.logger.debug("Input yaml: %s", len(yaml_str))
        _d = safe_load(yaml_str)
        return cls(_d)

    @classmethod
    def from_file(cls, path: str):
        """从文件加载配置"""
        cls.logger.debug("Input file: %s", path)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf8') as f:
                return cls.from_yaml(f.read())
        else:
            raise FileNotFoundError(f'文件不存在：{path}')

    def to_yaml(self):
        """转换为 YAML"""
        for key, value in self.items():
            logger.debug("DeParse %s: (%s)%s", key, type(value), value)
            if key in self._name_map:
                if isinstance(value, list):
                    self[key] = [dict(v) for v in value if isinstance(v, dict)]
                elif isinstance(value, dict):
                    self[key] = dict(value)
        return safe_dump(dict(self), allow_unicode=True, sort_keys=False)

    def save_yaml(self, file_path: str):
        """保存为 YAML"""
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(self.to_yaml())

    def set_port(self, port: int):
        """设置端口"""
        self['port'] = port

    @property
    def port(self):
        return self.get('port', 7890)

    def set_socks_port(self, port: int):
        """设置 SOCKS 端口"""
        self['socks-port'] = port

    @property
    def socks_port(self):
        return self.get('socks-port')

    def set_redir_port(self, port: int):
        """设置重定向端口"""
        self['redir-port'] = port

    @property
    def redir_port(self):
        return self.get('redir_port')

    def set_tproxy_port(self, port: bool):
        """设置是否开启 TProxy"""
        self['tproxy-port'] = port

    @property
    def tproxy_port(self):
        return self.get('tproxy-port')

    def set_mix_port(self, port: int):
        """设置混合端口"""
        self['mixed-port'] = port

    @property
    def mix_port(self):
        return self.get('mix-port')

    def set_authentication(self, username: str, password: str):
        """设置认证"""
        self['authentication'].add_auth(username, password)

    @property
    def authentication(self):
        return self.get('authentication', Authentication())

    def set_allow_lan(self, allow: bool):
        """设置是否允许局域网"""
        self['allow-lan'] = allow

    @property
    def allow_lan(self):
        return self.get('allow-lan', False)

    def set_bind_address(self, address: str):
        """设置绑定地址"""
        if self.get('allow-lan', False):
            raise ValueError('allow-lan is False, bind-address is not allowed')
        self['bind-address'] = address

    @property
    def bind_address(self):
        return self.get('bind-address', '127.0.0.1:7890')

    def set_mode(self, mode: str):
        """设置Clash运行模式

        rule: 规则模式
        global: 全局模式
        direct: 直连模式
        """
        self['mode'] = mode

    @property
    def mode(self):
        return self.get('mode', 'rule')

    def set_log_level(self, level: str):
        """设置日志等级

        silent: 不输出日志
        error: 只输出错误日志
        warning: 输出错误和警告日志
        info: 输出错误、警告和信息日志
        debug: 输出错误、警告、信息和调试日志
        """
        self['log-level'] = level

    @property
    def log_level(self):
        return self.get('log-level', 'info')

    def set_ipv6(self, ipv6: bool):
        """是否运行Ipv6支持"""
        self['ipv6'] = ipv6

    @property
    def ipv6(self):
        return self.get('ipv6')

    def set_external_controller(self, address: str, port: int = 9000):
        """设置外部控制器, RESTful web api 监听地址。

        :param address: 地址
        :param port: 端口
        """
        if len(address.split(':')) >= 2:
            self['external-controller'] = address
        else:
            self['external-controller'] = f'{address}:{port}'

    @property
    def external_controller(self):
        return self.get('external-controller')

    def set_external_ui(self, path):
        """外部控制UI
        WEB页面在文件系统中的位置
        """
        if os.path.exists(path) and os.path.isdir(path):
            self['external-ui'] = path
        raise FileNotFoundError(f'{path} 不存在或不是一个有效的目录')

    @property
    def external_ui(self):
        return self.get('external-ui')

    def set_secret(self, secret):
        """设置API访问秘钥"""
        if secret:
            self['secret'] = secret

    @property
    def secret(self):
        return self.get('secret')

    def set_interface_name(self, name):
        """设置全局出栈接口"""
        if not name:
            raise
        self['interface-name'] = name

    @property
    def interface_name(self):
        return self.get('interface-name')

    def set_routing_mark(self, mark=6666):
        if os.name == 'nt':
            raise OSError('Linux Only')
        self['routing-mark'] = mark

    def routing_mark(self):
        return self.get('routing-mark')

    def add_host(self, host, ip):
        """添加一个 静态Host        """
        self.get('hosts', dict())[host] = ip

    @property
    def hosts(self):
        return self.get('hosts', dict())

    def set_profile(self, profile: str, selected=False):
        pass

    # TODO get profile

    def add_proxy(self, proxy: Proxy):
        """添加一个代理"""
        if not isinstance(proxy, Proxy):
            raise TypeError('proxy must be a Proxy instance')
        self.get('proxies', list()).append(proxy)

    def del_proxy(self, proxy: Proxy):
        """删除一个代理"""
        if not isinstance(proxy, Proxy):
            raise TypeError('proxy must be a Proxy instance')
        self.get('proxies', list()).remove(proxy)

    def get_proxy(self, name: str):
        """获取一个代理"""
        for proxy in self.get('proxies', list()):
            if proxy.name == name:
                return proxy
        return None

    @property
    def proxies(self):
        """获取所有代理"""
        return self.get('proxies', list())

    def add_proxy_group(self, group: ProxyGroup):
        """添加一个代理组"""
        if not isinstance(group, ProxyGroup):
            raise TypeError('group must be a ProxyGroup instance')
        self.get('proxy-groups', list()).append(group)

    def del_proxy_group(self, group: ProxyGroup):
        """删除一个代理组"""
        if not isinstance(group, ProxyGroup):
            raise TypeError('group must be a ProxyGroup instance')
        self.get('proxy-groups', list()).remove(group)

    def get_proxy_group(self, name: str):
        """获取一个代理组"""
        for group in self.get('proxy-groups', list()):
            if group.name == name:
                return group
        return None

    @property
    def proxy_groups(self):
        """获取所有代理组"""
        return self.get('proxy-groups', list())

    def add_proxy_provider(self, proxy_provider: ProxyProvider):
        """添加一个代理提供者"""
        if not isinstance(proxy_provider, ProxyProvider):
            raise TypeError('proxy_provider must be a ProxyProvider instance')
        self.get('proxy-providers', list()).append(proxy_provider)

    def get_proxy_provider(self, name: str):
        """获取一个代理提供者"""
        for provider in self.get('proxy-providers', list()):
            if provider.name == name:
                return provider
        return None

    @property
    def proxy_providers(self):
        """获取所有代理提供者"""
        return self.get('proxy-providers', list())

    def del_proxy_provider(self, proxy_provider: ProxyProvider):
        """删除一个代理提供者"""
        if not isinstance(proxy_provider, ProxyProvider):
            raise TypeError('proxy_provider must be a ProxyProvider instance')
        self.get('proxy-providers', list()).remove(proxy_provider)

    def add_tunnel(self, tunnel: Tunnel):
        """添加一个隧道"""
        if not isinstance(tunnel, Tunnel):
            raise TypeError('tunnel must be a Tunnel instance')
        self.get('tunnels', list()).append(tunnel)

    def del_tunnel(self, tunnel: Tunnel):
        """删除一个隧道"""
        if not isinstance(tunnel, Tunnel):
            raise TypeError('tunnel must be a Tunnel instance')
        self.get('tunnels', list()).remove(tunnel)

    def get_tunnel(self, name: str):
        """获取一个隧道"""
        for tunnel in self.get('tunnels', list()):
            if tunnel.name == name:
                return tunnel
        return None

    def add_rule(self, rule: str):
        """添加一个规则"""
        if not isinstance(rule, str):
            raise TypeError('rule must be a Rule instance')
        self.get('rules', list()).append(rule)

    def del_rule(self, rule: str):
        """删除一个规则"""
        if not isinstance(rule, str):
            raise TypeError('rule must be a Rule instance')
        self.get('rules', list()).remove(rule)

    def get_rule(self, name: str):
        """获取一个规则"""
        for rule in self.get('rules', list()):
            if rule.name == name:
                return rule
        return None

    @property
    def rules(self):
        """获取所有规则"""
        return self.get('rules', list())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c = ConfigParse.from_file('../tests/clash_config/sub_config.yml')
    open('test.yml', 'w', encoding='utf8').write(c.to_yaml())
