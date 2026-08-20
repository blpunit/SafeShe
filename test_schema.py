import asyncio
from app.models.community import CommunityReport
from app.schemas.community_schemas import CommunityReportResponse

async def test():
    report = CommunityReport(
        report_type="Construction",
        location={"type":"Point", "coordinates": [0,0]}
    )
    print("report:", report.model_dump())
    print("report by_alias:", report.model_dump(by_alias=True))
    
    resp = CommunityReportResponse.model_validate(report.model_dump(by_alias=True))
    print("resp:", resp.model_dump())
    print("resp by_alias:", resp.model_dump(by_alias=True))

if __name__ == "__main__":
    asyncio.run(test())
