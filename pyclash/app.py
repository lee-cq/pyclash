#!/bin/env python3
from typing import Union

import uvicorn
from fastapi import FastAPI
from .apis import rules
from .apis import rule_providers

app = FastAPI(title='pyclash',)


@app.get('/')
def hello():
    return {'hello': 'fastapi'}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Rules Proxy -
app.include_router(router=rules.router, prefix='/rules')
app.include_router(router=rule_providers.router, prefix='/rule-providers')

if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8080)
