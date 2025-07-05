from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

financial_report_router = APIRouter()


@financial_report_router.post("/analyze_document")
async def analyze_document(request: Request, biz_type: str = ""):
    try:
        data = await request.json()
        if biz_type != "financial_report" or "content" not in data:
            return JSONResponse(
                status_code=400,
                content={"success": False, "msg": "参数错误"},
            )
        # 这里可接入真实分析逻辑，暂用 mock
        return {"success": True, "summary": "模拟财报分析结果", "biz_type": biz_type}
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "summary": "模拟财报分析结果",
                "biz_type": biz_type,
                "msg": str(e),
            },
        )
