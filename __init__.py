from jqdatasdk import *
import configparser

config = configparser.ConfigParser()
config.read("jq.conf", encoding="utf-8")
auth(config.get('jq', 'id'), config.get('jq', 'passwd'))
cache_root_path = config.get('jq', 'cacheRootPath')

