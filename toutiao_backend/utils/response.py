from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


def success_response(message:str="sucess",data=None):
	content={
		"code":200,
		"message":message,
		"data":data,
	}
	return JSONResponse(content=jsonable_encoder(content))
#jsonable_encoder:把任何FastAPI，Pydantic，ORM对象转换成可以被JSON安全序列化的数据结构
#因为data的类型不知道，如果直接return会报错，必须能够解析data对象。