"""
IT 기술 블로그 HTML 템플릿 생성 서비스
- 티스토리 블로그에 최적화된 HTML 템플릿
- 인라인 스타일 적용
- 반응형 디자인
"""

from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TechBlogTemplateService:
    """IT 기술 블로그 HTML 템플릿 서비스"""
    
    def __init__(self):
        pass
    
    def _clean_markdown_from_content(self, content: str) -> str:
        """마크다운 코드 블록 및 문법 제거"""
        import re
        
        # 1. 전체 문자열에서 ```html 제거
        content = content.replace('```html', '')
        content = content.replace('```html\n', '')
        content = content.replace('\n```html', '')
        
        # 2. 정규표현식으로 모든 ``` 패턴 제거
        content = re.sub(r'```html\s*', '', content)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        
        # 3. 줄 단위로 처리
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # ``` 만 있는 줄은 건너뛰기
            if stripped == '```' or stripped == '```html':
                continue
            
            # ``` 로 시작하는 줄도 건너뛰기
            if stripped.startswith('```'):
                continue
            
            # 줄 안에 남아있는 ``` 제거
            line = line.replace('```html', '')
            line = line.replace('```', '')
            
            # 줄 끝의 ``` 제거
            line = re.sub(r'```\s*$', '', line)
            
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # 4. 마지막으로 남아있는 ``` 제거
        result = re.sub(r'```', '', result)
        
        return result.strip()
    
    def generate_single_tech_template(self, tech_name: str, tech_type: str, content: str) -> str:
        """단일 기술 블로그 HTML 템플릿 생성"""
        
        # 마크다운 제거
        content = self._clean_markdown_from_content(content)
        
        template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tech_name} 완벽 가이드 - IT 기술 블로그</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
            font-style: italic;
        }}
        .meta-info {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
            font-size: 0.9em;
            color: #555;
        }}
        .meta-info span {{
            margin-right: 20px;
        }}
        .meta-info .tech-type {{
            background-color: #007bff;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }}
        h2 {{
            color: #007bff;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }}
        h3 {{
            color: #495057;
            font-size: 1.2em;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        .code-block {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .tag {{
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{tech_name}</h1>
            <div class="subtitle">완벽 가이드</div>
        </div>
        
        <div class="meta-info">
            <span><strong>기술 분야:</strong> <span class="tech-type">{tech_type}</span></span>
            <span><strong>작성일:</strong> {datetime.now().strftime('%Y년 %m월 %d일')}</span>
            <span><strong>분류:</strong> IT 기술 블로그</span>
        </div>
        
        <div class="content">
{content}
        </div>
        
        <div class="footer">
            <div class="tags">
                <span class="tag">{tech_name}</span>
                <span class="tag">{tech_type}</span>
                <span class="tag">IT기술</span>
                <span class="tag">프로그래밍</span>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
    
    def generate_comparison_template(self, tech1_name: str, tech2_name: str, tech_type: str, content: str) -> str:
        """기술 비교 블로그 HTML 템플릿 생성"""
        
        # 마크다운 제거
        content = self._clean_markdown_from_content(content)
        
        template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tech1_name} vs {tech2_name} 완벽 비교 - IT 기술 블로그</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #28a745;
        }}
        .header h1 {{
            color: #28a745;
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
            font-style: italic;
        }}
        .comparison-badge {{
            display: inline-block;
            background: linear-gradient(45deg, #007bff, #28a745);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .meta-info {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
            font-size: 0.9em;
            color: #555;
        }}
        .meta-info span {{
            margin-right: 20px;
        }}
        .meta-info .tech-type {{
            background-color: #28a745;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }}
        h2 {{
            color: #28a745;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }}
        h3 {{
            color: #495057;
            font-size: 1.2em;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        .tech1-title {{
            color: #007bff;
            border-left: 4px solid #007bff;
            padding-left: 10px;
        }}
        .tech2-title {{
            color: #dc3545;
            border-left: 4px solid #dc3545;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #28a745;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e9ecef;
        }}
        .vs-highlight {{
            background: linear-gradient(90deg, #007bff20, #dc354520);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #28a745;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .tag {{
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
            table {{
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{tech1_name} vs {tech2_name}</h1>
            <div class="subtitle">완벽 비교 분석</div>
            <div class="comparison-badge">기술 비교</div>
        </div>
        
        <div class="meta-info">
            <span><strong>비교 분야:</strong> <span class="tech-type">{tech_type}</span></span>
            <span><strong>작성일:</strong> {datetime.now().strftime('%Y년 %m월 %d일')}</span>
            <span><strong>분류:</strong> IT 기술 비교</span>
        </div>
        
        <div class="vs-highlight">
            <h3 style="text-align: center; margin-top: 0; color: #28a745;">
                {tech1_name} vs {tech2_name} - 어떤 것을 선택해야 할까요?
            </h3>
        </div>
        
        <div class="content">
{content}
        </div>
        
        <div class="footer">
            <div class="tags">
                <span class="tag">{tech1_name}</span>
                <span class="tag">{tech2_name}</span>
                <span class="tag">{tech_type}</span>
                <span class="tag">기술비교</span>
                <span class="tag">IT기술</span>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
    
    def generate_algorithm_template(self, algorithm_name: str, algorithm_type: str, content: str) -> str:
        """알고리즘 블로그 HTML 템플릿 생성"""
        
        # 마크다운 제거
        content = self._clean_markdown_from_content(content)
        
        template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{algorithm_name} 완벽 가이드 - 알고리즘 블로그</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #6f42c1;
        }}
        .header h1 {{
            color: #6f42c1;
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
            font-style: italic;
        }}
        .algorithm-badge {{
            display: inline-block;
            background: linear-gradient(45deg, #6f42c1, #e83e8c);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .meta-info {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
            font-size: 0.9em;
            color: #555;
        }}
        .meta-info span {{
            margin-right: 20px;
        }}
        .meta-info .algorithm-type {{
            background-color: #6f42c1;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }}
        h2 {{
            color: #6f42c1;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }}
        h3 {{
            color: #495057;
            font-size: 1.2em;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        .code-block {{
            background-color: #2d3748;
            color: #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .code-block .comment {{
            color: #68d391;
        }}
        .code-block .keyword {{
            color: #f687b3;
        }}
        .code-block .string {{
            color: #fbb6ce;
        }}
        .complexity {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        .complexity h4 {{
            margin-top: 0;
            color: #856404;
        }}
        .step-by-step {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        .step-by-step ol {{
            margin: 0;
            padding-left: 20px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .tag {{
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
            .code-block {{
                font-size: 0.8em;
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{algorithm_name}</h1>
            <div class="subtitle">완벽 가이드</div>
            <div class="algorithm-badge">알고리즘</div>
        </div>
        
        <div class="meta-info">
            <span><strong>분류:</strong> <span class="algorithm-type">{algorithm_type}</span></span>
            <span><strong>작성일:</strong> {datetime.now().strftime('%Y년 %m월 %d일')}</span>
            <span><strong>카테고리:</strong> 알고리즘 블로그</span>
        </div>
        
        <div class="content">
{content}
        </div>
        
        <div class="footer">
            <div class="tags">
                <span class="tag">{algorithm_name}</span>
                <span class="tag">{algorithm_type}</span>
                <span class="tag">알고리즘</span>
                <span class="tag">Java</span>
                <span class="tag">프로그래밍</span>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
