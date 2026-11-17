from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

root = Path('/home/bikmetle/projects/cv')
source = (root / 'ru/cv-ru.txt').read_text()
for name, file in [('CV','DejaVuSans.ttf'),('CVBold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/' + file))
ink = colors.HexColor('#182535')
muted = colors.HexColor('#506275')
styles = {
    'body': ParagraphStyle('body', fontName='CV', fontSize=9.2, leading=11.8, textColor=ink, spaceAfter=3),
    'bullet': ParagraphStyle('bullet', fontName='CV', fontSize=9.2, leading=11.8, textColor=ink, leftIndent=11, firstLineIndent=-9, spaceAfter=3),
    'name': ParagraphStyle('name', fontName='CVBold', fontSize=23, leading=29, textColor=ink, spaceAfter=3),
    'role': ParagraphStyle('role', fontName='CV', fontSize=11, leading=16, textColor=muted, spaceAfter=12),
    'section': ParagraphStyle('section', fontName='CVBold', fontSize=11, leading=16, textColor=muted, spaceBefore=10, spaceAfter=6, keepWithNext=True),
    'job': ParagraphStyle('job', fontName='CVBold', fontSize=10.6, leading=15, textColor=ink, spaceBefore=9, spaceAfter=4, keepWithNext=True),
    'label': ParagraphStyle('label', fontName='CVBold', fontSize=9.2, leading=11.8, textColor=ink, spaceBefore=6, spaceAfter=4, keepWithNext=True),
}
sections = {'ПРОФИЛЬ','КЛЮЧЕВЫЕ НАВЫКИ (ключевые слова для ATS)','ОПЫТ РАБОТЫ','ОБРАЗОВАНИЕ','ЯЗЫКИ','ДОПОЛНИТЕЛЬНО','КЛЮЧЕВЫЕ ДОСТИЖЕНИЯ'}
blocks=[]
current=[]
def flush():
    if current:
        blocks.append(' '.join(current))
        current.clear()
for line in source.splitlines():
    stripped=line.strip()
    if not stripped or re.fullmatch(r'[═─.]+', stripped):
        flush()
        continue
    special = stripped in sections or stripped in ('Обязанности:', 'Достижения:') or stripped.startswith(('DevMark —', 'Доброфон —', '- ', 'Стек:', 'Телефон:', 'Email:', 'Telegram:', 'Локация:', 'Гражданство:', 'Ожидания:', 'Ноябрь 2023', 'Сентябрь 2022', 'Русский —', 'Английский —', 'Арабский —', 'Индонезийский —', 'Турецкий —', 'Испанский —'))
    if special:
        flush()
    current.append(stripped)
    if stripped in sections or stripped in ('Обязанности:', 'Достижения:') or stripped.startswith(('DevMark —', 'Доброфон —', 'Ноябрь 2023', 'Сентябрь 2022', 'Телефон:', 'Email:', 'Telegram:', 'Локация:', 'Гражданство:', 'Ожидания:', 'Русский —', 'Английский —', 'Арабский —', 'Индонезийский —', 'Турецкий —', 'Испанский —')):
        flush()
flush()
story=[]
# The first block contains the name and professional headline.
header = blocks.pop(0)
name, role = header.split('Backend-разработчик', 1)
story += [Paragraph(escape(name.strip()), styles['name']), Paragraph(escape('Backend-разработчик'+role), styles['role'])]
for block in blocks:
    if block.startswith('DevMark — Backend Developer / Feature Lead, AI') or block == 'ОБРАЗОВАНИЕ':
        story.append(PageBreak())
    kind='body'
    if block in sections: kind='section'
    elif block.startswith(('DevMark —', 'Доброфон —')): kind='job'
    elif block in ('Обязанности:', 'Достижения:'): kind='label'
    elif block.startswith('- '): kind='bullet'
    block=block.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    story.append(Paragraph(escape(block), styles[kind]))
output=root/'output/pdf/cv-ru.pdf'
def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#D8DFE6'))
    canvas.line(42,35,A4[0]-42,35)
    canvas.setFont('CV',8)
    canvas.setFillColor(muted)
    canvas.drawString(42,23,'Марсель Гайфуллин | Backend Developer')
    canvas.drawRightString(A4[0]-42,23,str(doc.page))
doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=35,bottomMargin=48,title='Марсель Гайфуллин - Backend Developer',author='Марсель Гайфуллин')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(output)
print('Pages:',len(reader.pages))
for i,page in enumerate(reader.pages,1):
    text=page.extract_text()
    print(i,len(text),text[:95].replace('\n',' | '))
extracted=' '.join(p.extract_text() for p in reader.pages)
normalize=lambda s: re.sub(r'\s+','',s.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-'))
for block in blocks:
    assert normalize(block) in normalize(extracted), block
print('All source paragraphs verified in PDF')
