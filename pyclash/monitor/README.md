# Loki 接收数据结构

```json
{
  "streams": [
    {
      "labels": "{source=\"Name-of-your-source\",job=\"name-of-your-job\", host=\"",
      "entries": [
        {
          "ts": "curr_datetime",
          "line": "[WARN] msg"
        }
      ]
    }
  ]
}
```

# Put返回文档

```python
log_queue.put(
    {'timestamp': time.time_ns(),
     'name': urlparse.path.split('/')[-1],
     'host': urlparse.netloc,
     'from_url': ws_client.url,
     'message': message
     }, block=False)
```

# 监控类型关系处理

## 1. traffic

原始文档

```json
{
  "timestamp": 1676119488207053056,
  "name": "c",
  "host": "192.168.0.4:29090",
  "from_url": "ws://192.168.0.4:29090/traffic?token=123456&level=DEBUG",
  "message": {
    "up": 0,
    "down": 0
  }
}
```

目标文档

```json
{
  "streams": [
    {
      "stream": {
        "type": "traffic"
      },
      "values": [
        [
          "1676115649304780350",
          "{\"down\":0,\"type\":\"traffic\",\"up\":0}"
        ],
        [
          "1676115650298849359",
          "{\"down\":0,\"type\":\"traffic\",\"up\":0}"
        ]
      ]
    }
  ]
}
```

## 2. profile/tracing

### 2.1. RuleMatch

原始文档

```json
{
  "timestamp": 1676118392691968256,
  "name": "g",
  "host": "192.168.0.4:29090",
  "from_url": "ws://192.168.0.4:29090/profile/tracing?token=123456&level=DEBUG",
  "message": {
    "duration": 22,
    "id": "ea283172-8124-4ffc-bdce-abc026b70a55",
    "metadata": {
      "network": "tcp",
      "type": "Socks5",
      "sourceIP": "192.168.0.55",
      "destinationIP": "",
      "sourcePort": "52557",
      "destinationPort": "443",
      "host": "firestore.googleapis.com",
      "dnsMode": "normal",
      "processPath": "",
      "specialProxy": ""
    },
    "payload": "",
    "proxy": "DIRECT",
    "rule": "Match",
    "type": "RuleMatch"
  }
}
```

目标文档

```json
{
  "streams": [
    {
      "stream": {
        "type": "rulematch"
      },
      "values": [
        [
          "1676118292233029243",
          {
            "duration": 32,
            "id": "fe39b1dd-6d3c-41a6-bb07-a35564e07a0f",
            "metadata_dnsmode": "normal",
            "metadata_dstip": "",
            "metadata_dstport": "443",
            "metadata_host": "github.com",
            "metadata_network": "tcp",
            "metadata_srcip": "192.168.0.55",
            "metadata_srcport": "52397",
            "metadata_type": "Socks5",
            "payload": "github.com",
            "proxy": "github",
            "rule": "DomainSuffix",
            "type": "rulematch"
          }
        ],
        [
          "1676118292233058964",
          {
            "duration": 13,
            "id": "94933802-728e-4743-a972-98b40b9d2bd1",
            "metadata_dnsmode": "normal",
            "metadata_dstip": "",
            "metadata_dstport": "443",
            "metadata_host": "github.githubassets.com",
            "metadata_network": "tcp",
            "metadata_srcip": "192.168.0.55",
            "metadata_srcport": "52398",
            "metadata_type": "Socks5",
            "payload": "github",
            "proxy": "github",
            "rule": "RuleSet",
            "type": "rulematch"
          }
        ]
      ]
    }
  ]
}
```

### 2.2. Proxyal

原始文档

```json
{
  "timestamp": 1676118392689949696,
  "name": "g",
  "host": "192.168.0.4:29090",
  "from_url": "ws://192.168.0.4:29090/profile/tracing?token=123456&level=DEBUG",
  "message": {
    "address": "firestore.googleapis.com:443",
    "duration": 5000748,
    "error": "dial tcp4 142.250.66.74:443: i/o timeout",
    "host": "firestore.googleapis.com",
    "id": "dc888fd2-ec48-4879-ad90-ede09e6b1abb",
    "proxy": "DIRECT",
    "type": "ProxyDial"
  }
}

```

目标文档

```json
{
  "streams": [
    {
      "stream": {
        "type": "proxydial"
      },
      "values": [
        [
          "1676119017699008055",
          {
            "address": "firestore.googleapis.com:443",
            "duration": 5000765,
            "error": "dial tcp4 142.250.191.42:443: i/o timeout",
            "host": "firestore.googleapis.com",
            "id": "fd3ae520-119b-4ef3-80a7-8f92a6e845a5",
            "proxy": "DIRECT",
            "type": "proxydial"
          }
        ]
      ]
    }
  ]
}
```