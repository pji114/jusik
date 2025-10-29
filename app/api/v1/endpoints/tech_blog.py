"""
IT 기술 블로그 API 엔드포인트
- 단일 기술 설명
- 기술 비교
- 알고리즘/자료구조/디자인 패턴 설명
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Optional
import logging
from datetime import datetime

from app.services.tech_blog_service import TechBlogService
from app.services.tech_blog_template_service import TechBlogTemplateService
from app.core.exceptions import create_http_exception

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/single-tech", response_class=HTMLResponse)
async def generate_single_tech_blog(
    tech_name: str = Query(..., description="기술명 (예: EKS, Security Hub, React)"),
    tech_type: str = Query("general", description="기술 유형 (general, cloud, frontend, backend, database)"),
    save_file: bool = Query(False, description="HTML 파일로 저장 여부")
):
    """
    단일 기술에 대한 블로그 생성
    
    - **tech_name**: 기술명 (예: EKS, Security Hub, React)
    - **tech_type**: 기술 유형 (general, cloud, frontend, backend, database)
    - **save_file**: HTML 파일로 저장 여부
    
    반환되는 HTML은 다음 구조로 구성됩니다:
    1. 기술의 정의
    2. 기술의 탄생배경
    3. 기술의 특징
    4. 실제 사용 예시
    5. 코드 예시
    """
    try:
        tech_blog_service = TechBlogService()
        template_service = TechBlogTemplateService()
        
        # AI를 통한 블로그 내용 생성
        blog_content = await tech_blog_service.generate_single_tech_blog(
            tech_name=tech_name,
            tech_type=tech_type
        )
        
        # HTML 템플릿 적용 (템플릿 내부에서 마크다운 제거됨)
        html_content = template_service.generate_single_tech_template(
            tech_name=tech_name,
            tech_type=tech_type,
            content=blog_content
        )
        
        # 파일 저장 (선택사항)
        if save_file:
            file_path = tech_blog_service.save_tech_blog_html(
                blog_content=html_content,
                tech_name=tech_name,
                blog_type="single"
            )
            logger.info(f"단일 기술 블로그 저장 완료: {file_path}")
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"단일 기술 블로그 생성 실패: {e}")
        raise create_http_exception(e)


@router.post("/single-tech/save")
async def save_single_tech_blog(
    tech_name: str = Query(..., description="기술명"),
    tech_type: str = Query("general", description="기술 유형"),
    tech_blog_service: TechBlogService = Depends(),
    template_service: TechBlogTemplateService = Depends()
):
    """
    단일 기술 블로그 생성 및 파일 저장
    
    - **tech_name**: 기술명
    - **tech_type**: 기술 유형
    
    HTML 파일이 report/ 폴더에 저장됩니다.
    """
    try:
        # AI를 통한 블로그 내용 생성
        blog_content = await tech_blog_service.generate_single_tech_blog(
            tech_name=tech_name,
            tech_type=tech_type
        )
        
        # HTML 템플릿 적용 (템플릿 내부에서 마크다운 제거됨)
        html_content = template_service.generate_single_tech_template(
            tech_name=tech_name,
            tech_type=tech_type,
            content=blog_content
        )
        
        # 파일 저장
        file_path = tech_blog_service.save_tech_blog_html(
            blog_content=html_content,
            tech_name=tech_name,
            blog_type="single"
        )
        
        return {
            "message": f"단일 기술 블로그 생성 및 저장 완료: {tech_name}",
            "file_path": file_path,
            "tech_name": tech_name,
            "tech_type": tech_type,
            "blog_type": "single",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"단일 기술 블로그 저장 실패: {e}")
        raise create_http_exception(e)


@router.get("/tech-comparison", response_class=HTMLResponse)
async def generate_tech_comparison_blog(
    tech1_name: str = Query(..., description="첫 번째 기술명"),
    tech2_name: str = Query(..., description="두 번째 기술명"),
    comparison_type: str = Query("general", description="비교 유형 (general, cloud, framework, database)"),
    save_file: bool = Query(False, description="HTML 파일로 저장 여부")
):
    """
    두 기술에 대한 비교 블로그 생성
    
    - **tech1_name**: 첫 번째 기술명
    - **tech2_name**: 두 번째 기술명
    - **comparison_type**: 비교 유형
    - **save_file**: HTML 파일로 저장 여부
    
    반환되는 HTML은 다음 구조로 구성됩니다:
    1. 각 기술에 대한 정의
    2. 각 기술의 특징
    3. 기술 비교 도표 (표 형태)
    4. 각 기술의 사용 예시
    """
    try:
        tech_blog_service = TechBlogService()
        template_service = TechBlogTemplateService()
        
        # AI를 통한 비교 블로그 내용 생성
        blog_content = await tech_blog_service.generate_tech_comparison_blog(
            tech1_name=tech1_name,
            tech2_name=tech2_name,
            comparison_type=comparison_type
        )
        
        # HTML 템플릿 적용
        html_content = template_service.generate_comparison_template(
            tech1_name=tech1_name,
            tech2_name=tech2_name,
            tech_type=comparison_type,
            content=blog_content
        )
        
        # 파일 저장 (선택사항)
        if save_file:
            comparison_name = f"{tech1_name}_vs_{tech2_name}"
            file_path = tech_blog_service.save_tech_blog_html(
                blog_content=html_content,
                tech_name=comparison_name,
                blog_type="comparison"
            )
            logger.info(f"기술 비교 블로그 저장 완료: {file_path}")
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"기술 비교 블로그 생성 실패: {e}")
        raise create_http_exception(e)


@router.post("/tech-comparison/save")
async def save_tech_comparison_blog(
    tech1_name: str = Query(..., description="첫 번째 기술명"),
    tech2_name: str = Query(..., description="두 번째 기술명"),
    comparison_type: str = Query("general", description="비교 유형"),
    tech_blog_service: TechBlogService = Depends(),
    template_service: TechBlogTemplateService = Depends()
):
    """
    기술 비교 블로그 생성 및 파일 저장
    
    - **tech1_name**: 첫 번째 기술명
    - **tech2_name**: 두 번째 기술명
    - **comparison_type**: 비교 유형
    
    HTML 파일이 report/ 폴더에 저장됩니다.
    """
    try:
        # AI를 통한 비교 블로그 내용 생성
        blog_content = await tech_blog_service.generate_tech_comparison_blog(
            tech1_name=tech1_name,
            tech2_name=tech2_name,
            comparison_type=comparison_type
        )
        
        # HTML 템플릿 적용
        html_content = template_service.generate_comparison_template(
            tech1_name=tech1_name,
            tech2_name=tech2_name,
            tech_type=comparison_type,
            content=blog_content
        )
        
        # 파일 저장
        comparison_name = f"{tech1_name}_vs_{tech2_name}"
        file_path = tech_blog_service.save_tech_blog_html(
            blog_content=html_content,
            tech_name=comparison_name,
            blog_type="comparison"
        )
        
        return {
            "message": f"기술 비교 블로그 생성 및 저장 완료: {tech1_name} vs {tech2_name}",
            "file_path": file_path,
            "tech1_name": tech1_name,
            "tech2_name": tech2_name,
            "comparison_type": comparison_type,
            "blog_type": "comparison",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"기술 비교 블로그 저장 실패: {e}")
        raise create_http_exception(e)


@router.get("/algorithm", response_class=HTMLResponse)
async def generate_algorithm_blog(
    algorithm_name: str = Query(..., description="알고리즘명 (예: BFS, JPA N+1 문제, 다이아몬드 상속)"),
    algorithm_type: str = Query("algorithm", description="알고리즘 유형 (algorithm, data_structure, design_pattern, problem)"),
    save_file: bool = Query(False, description="HTML 파일로 저장 여부")
):
    """
    알고리즘/자료구조/디자인 패턴 블로그 생성
    
    - **algorithm_name**: 알고리즘명
    - **algorithm_type**: 알고리즘 유형
    - **save_file**: HTML 파일로 저장 여부
    
    반환되는 HTML은 다음 구조로 구성됩니다:
    1. 알고리즘의 정의
    2. 알고리즘의 특징
    3. 알고리즘 동작 원리
    4. Java 코드 예제
    5. 실제 사용 예시
    """
    try:
        tech_blog_service = TechBlogService()
        template_service = TechBlogTemplateService()
        
        # AI를 통한 알고리즘 블로그 내용 생성
        blog_content = await tech_blog_service.generate_algorithm_blog(
            algorithm_name=algorithm_name,
            algorithm_type=algorithm_type
        )
        
        # HTML 템플릿 적용
        html_content = template_service.generate_algorithm_template(
            algorithm_name=algorithm_name,
            algorithm_type=algorithm_type,
            content=blog_content
        )
        
        # 파일 저장 (선택사항)
        if save_file:
            file_path = tech_blog_service.save_tech_blog_html(
                blog_content=html_content,
                tech_name=algorithm_name,
                blog_type="algorithm"
            )
            logger.info(f"알고리즘 블로그 저장 완료: {file_path}")
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"알고리즘 블로그 생성 실패: {e}")
        raise create_http_exception(e)


@router.post("/algorithm/save")
async def save_algorithm_blog(
    algorithm_name: str = Query(..., description="알고리즘명"),
    algorithm_type: str = Query("algorithm", description="알고리즘 유형"),
    tech_blog_service: TechBlogService = Depends(),
    template_service: TechBlogTemplateService = Depends()
):
    """
    알고리즘 블로그 생성 및 파일 저장
    
    - **algorithm_name**: 알고리즘명
    - **algorithm_type**: 알고리즘 유형
    
    HTML 파일이 report/ 폴더에 저장됩니다.
    """
    try:
        # AI를 통한 알고리즘 블로그 내용 생성
        blog_content = await tech_blog_service.generate_algorithm_blog(
            algorithm_name=algorithm_name,
            algorithm_type=algorithm_type
        )
        
        # HTML 템플릿 적용
        html_content = template_service.generate_algorithm_template(
            algorithm_name=algorithm_name,
            algorithm_type=algorithm_type,
            content=blog_content
        )
        
        # 파일 저장
        file_path = tech_blog_service.save_tech_blog_html(
            blog_content=html_content,
            tech_name=algorithm_name,
            blog_type="algorithm"
        )
        
        return {
            "message": f"알고리즘 블로그 생성 및 저장 완료: {algorithm_name}",
            "file_path": file_path,
            "algorithm_name": algorithm_name,
            "algorithm_type": algorithm_type,
            "blog_type": "algorithm",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"알고리즘 블로그 저장 실패: {e}")
        raise create_http_exception(e)


@router.get("/status")
async def get_tech_blog_status():
    """
    IT 기술 블로그 서비스 상태 확인
    """
    try:
        return {
            "status": "active",
            "service": "IT Tech Blog Service",
            "available_endpoints": [
                "GET /single-tech - 단일 기술 블로그 생성",
                "POST /single-tech/save - 단일 기술 블로그 저장",
                "GET /tech-comparison - 기술 비교 블로그 생성",
                "POST /tech-comparison/save - 기술 비교 블로그 저장",
                "GET /algorithm - 알고리즘 블로그 생성",
                "POST /algorithm/save - 알고리즘 블로그 저장"
            ],
            "supported_tech_types": [
                "general", "cloud", "frontend", "backend", "database",
                "algorithm", "data_structure", "design_pattern", "problem"
            ],
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        raise create_http_exception(e)
