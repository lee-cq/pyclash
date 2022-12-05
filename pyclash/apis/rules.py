from enum import Enum
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()



class RuleTypeEume(str, Enum):
    DOMAIN_SUFFIX = 'DOMAIN-SUFFIX'
    DOMAIN_KEYWORD = 'DOMAIN-KEYWORD'
    DOMAIN = 'DOMAIN'
    SRC_IP_CIDR = 'SRC-IP-CIDR'
    IP_CIDR = 'IP-CIDR'
    IP_CIDR6 = 'IP-CIDR6'
    GEOIP = 'GEOIP'
    DST_PORT = 'DST-PORT'
    SRC_PORT = 'SRC-PORT'
    MATCH = 'MATCH'


class RuleClassical(BaseModel):
    type: RuleTypeEume
    payload: str

class Rule(RuleClassical):
    proxy: str


@router.post('self/proxy')
def self_rule_proxy_add(type: RuleTypeEume, payload: str = None):
    """新增自定义代理域名"""

    return {}


@router.get('self/proxy')
def self_rule_proxy_list():

    return {}


@router.delete('self/proxy')
def self_rule_proxy_del():
    return {}

# Rules direct


@router.post('self/direct')
def self_rule_direct_add(type: RuleTypeEume, payload: str = None):
    return {}


@router.get('self/direct')
def self_rule_direct_list(rule: str):
    return {}


@router.delete('self/direct')
def self_rule_direct_del():
    return {}
