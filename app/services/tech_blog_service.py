"""
IT 기술 블로그 서비스
- 단일 기술 설명
- 기술 비교
- 알고리즘/자료구조/디자인 패턴 설명
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.exceptions import OpenAIException
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class TechBlogService:
    """IT 기술 블로그 생성 서비스"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def _clean_unwanted_explanations(self, content: str) -> str:
        """불필요한 메타 설명 제거"""
        import re
        
        # 다양한 불필요한 설명 패턴 제거
        unwanted_patterns = [
            r'이 블로그.*티스토리.*스타일.*작성.*',
            r'이 HTML 구조는.*티스토리.*최적화.*',
            r'각 섹션.*HTML 태그.*구조화.*',
            r'티스토리 블로그.*최적화.*스타일.*',
            r'블로그 포스트는.*설명.*포함.*구성.*',
            r'이 블로그는 AI를 활용하여 작성되었습니다\.',
            r'각 섹션은 HTML 태그를 사용하여 구조화되어 있으며.*',
            r'티스토리 블로그에 최적화된 인라인 스타일.*',
            r'.*티스토리.*블로그.*최적화.*'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # 줄 단위로도 제거
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # 불필요한 설명이 포함된 줄 건너뛰기
            if any(keyword in line for keyword in ['블로그는', 'HTML 구조는', '티스토리 블로그에 최적화', '각 섹션은 HTML']):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _clean_markdown_code_blocks(self, content: str) -> str:
        """마크다운 코드 블록 제거"""
        import re
        
        # 전체 내용에서 마크다운 코드 블록 시작/끝 제거
        content = re.sub(r'```html\s*', '', content)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        
        # 줄 단위로 처리
        lines = content.split('\n')
        cleaned_lines = []
        skip_next = False
        
        for line in lines:
            stripped = line.strip()
            
            # ``` 패턴만 있는 줄은 건너뛰기
            if re.match(r'^```\s*$', stripped):
                skip_next = True
                continue
            
            # 코드 블록 끝 감지
            if stripped == '```' and skip_next:
                skip_next = False
                continue
            
            # 라인 안에 ``` 가 있는 경우 제거
            if '```' in line:
                line = re.sub(r'```html\s*', '', line)
                line = re.sub(r'```\s*$', '', line)
                line = re.sub(r'```\s*', '', line)
            
            if not skip_next:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        
        # 마지막으로 남아있는 ``` 제거
        result = re.sub(r'```\s*$', '', result, flags=re.MULTILINE)
        
        return result
    
    async def generate_single_tech_blog(self, tech_name: str, tech_type: str = "general") -> str:
        """
        단일 기술에 대한 블로그 생성
        
        Args:
            tech_name: 기술명 (예: EKS, Security Hub, React)
            tech_type: 기술 유형 (general, cloud, frontend, backend, database, etc.)
        
        Returns:
            HTML 형태의 기술 블로그
        """
        try:
            logger.info(f"단일 기술 블로그 생성 시작: {tech_name}")
            
            # AI 서비스를 통한 기술 블로그 생성
            blog_content = await self.ai_service.generate_tech_blog(
                tech_name=tech_name,
                tech_type=tech_type,
                blog_type="single"
            )
            
            # 마크다운 코드 블록 제거
            blog_content = self._clean_markdown_code_blocks(blog_content)
            
            # 불필요한 메타 설명 제거
            blog_content = self._clean_unwanted_explanations(blog_content)
            
            logger.info(f"단일 기술 블로그 생성 완료: {tech_name}")
            return blog_content
            
        except Exception as e:
            logger.error(f"단일 기술 블로그 생성 실패 ({tech_name}): {e}")
            raise OpenAIException(f"기술 블로그 생성에 실패했습니다: {str(e)}")
    
    async def generate_tech_comparison_blog(self, tech1_name: str, tech2_name: str, comparison_type: str = "general") -> str:
        """
        두 기술에 대한 비교 블로그 생성
        
        Args:
            tech1_name: 첫 번째 기술명
            tech2_name: 두 번째 기술명
            comparison_type: 비교 유형 (general, cloud, framework, database, etc.)
        
        Returns:
            HTML 형태의 기술 비교 블로그
        """
        try:
            logger.info(f"기술 비교 블로그 생성 시작: {tech1_name} vs {tech2_name}")
            
            # AI 서비스를 통한 기술 비교 블로그 생성
            blog_content = await self.ai_service.generate_tech_blog(
                tech_name=tech1_name,
                tech2_name=tech2_name,
                tech_type=comparison_type,
                blog_type="comparison"
            )
            
            # 마크다운 코드 블록 제거
            blog_content = self._clean_markdown_code_blocks(blog_content)
            
            logger.info(f"기술 비교 블로그 생성 완료: {tech1_name} vs {tech2_name}")
            return blog_content
            
        except Exception as e:
            logger.error(f"기술 비교 블로그 생성 실패 ({tech1_name} vs {tech2_name}): {e}")
            raise OpenAIException(f"기술 비교 블로그 생성에 실패했습니다: {str(e)}")
    
    async def generate_algorithm_blog(self, algorithm_name: str, algorithm_type: str = "algorithm") -> str:
        """
        알고리즘/자료구조/디자인 패턴 블로그 생성
        
        Args:
            algorithm_name: 알고리즘명 (예: BFS, JPA N+1 문제, 다이아몬드 상속)
            algorithm_type: 알고리즘 유형 (algorithm, data_structure, design_pattern, problem)
        
        Returns:
            HTML 형태의 알고리즘 블로그
        """
        try:
            logger.info(f"알고리즘 블로그 생성 시작: {algorithm_name}")
            
            # AI 서비스를 통한 알고리즘 블로그 생성
            blog_content = await self.ai_service.generate_tech_blog(
                tech_name=algorithm_name,
                tech_type=algorithm_type,
                blog_type="algorithm"
            )
            
            # 마크다운 코드 블록 제거
            blog_content = self._clean_markdown_code_blocks(blog_content)
            
            logger.info(f"알고리즘 블로그 생성 완료: {algorithm_name}")
            return blog_content
            
        except Exception as e:
            logger.error(f"알고리즘 블로그 생성 실패 ({algorithm_name}): {e}")
            raise OpenAIException(f"알고리즘 블로그 생성에 실패했습니다: {str(e)}")
    
    def save_tech_blog_html(self, blog_content: str, tech_name: str, blog_type: str = "single") -> str:
        """
        기술 블로그 HTML 파일 저장
        
        Args:
            blog_content: 블로그 HTML 내용
            tech_name: 기술명
            blog_type: 블로그 유형 (single, comparison, algorithm)
        
        Returns:
            저장된 파일 경로
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 파일명 생성
            if blog_type == "comparison":
                filename = f"IT기술_비교_{tech_name}_{timestamp}.html"
            elif blog_type == "algorithm":
                filename = f"IT기술_알고리즘_{tech_name}_{timestamp}.html"
            else:
                filename = f"IT기술_단일_{tech_name}_{timestamp}.html"
            
            # 파일 저장
            file_path = f"report/{filename}"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(blog_content)
            
            logger.info(f"기술 블로그 HTML 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"기술 블로그 HTML 저장 실패: {e}")
            raise Exception(f"HTML 파일 저장에 실패했습니다: {str(e)}")
