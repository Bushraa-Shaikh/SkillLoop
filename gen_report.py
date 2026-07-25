from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import KeepTogether
import os

# ── Colors ──────────────────────────────────────────────────────
NAVY  = colors.HexColor('#0A0F1E')
TEAL  = colors.HexColor('#00A88A')
TEAL2 = colors.HexColor('#E1F5EE')
WHITE = colors.white
GRAY  = colors.HexColor('#F1F5F9')
DARK  = colors.HexColor('#1E2A3A')
AMBER = colors.HexColor('#F59E0B')
RED   = colors.HexColor('#EF4444')
BLUE  = colors.HexColor('#1E40AF')
MID   = colors.HexColor('#475569')

W, H = A4
MARGIN = 2*cm

def build_report():
    doc = SimpleDocTemplate(
        r'C:\Users\Bushra Shaikh\Desktop\SkillLoop_Architecture_Report.pdf',
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title='SkillLoop – Architecture Report',
        author='Bushra Shaikh'
    )

    styles = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    cover_title = S('ct', fontSize=42, textColor=NAVY, alignment=TA_CENTER,
                    fontName='Helvetica-Bold', spaceAfter=8)
    cover_sub   = S('cs', fontSize=18, textColor=TEAL, alignment=TA_CENTER,
                    fontName='Helvetica', spaceAfter=6)
    cover_info  = S('ci', fontSize=12, textColor=MID, alignment=TA_CENTER,
                    fontName='Helvetica', spaceAfter=4)
    h1_s = S('h1s', fontSize=20, textColor=NAVY, fontName='Helvetica-Bold',
              spaceBefore=18, spaceAfter=8, borderPad=4)
    h2_s = S('h2s', fontSize=15, textColor=TEAL, fontName='Helvetica-Bold',
              spaceBefore=14, spaceAfter=6)
    h3_s = S('h3s', fontSize=13, textColor=NAVY, fontName='Helvetica-Bold',
              spaceBefore=10, spaceAfter=5)
    body = S('body', fontSize=10, textColor=colors.HexColor('#222222'),
             fontName='Helvetica', spaceAfter=6, leading=15, alignment=TA_JUSTIFY)
    bullet_s = S('bul', fontSize=10, textColor=colors.HexColor('#333333'),
                 fontName='Helvetica', spaceAfter=4, leftIndent=16,
                 bulletIndent=6, leading=14)
    caption = S('cap', fontSize=9, textColor=MID, fontName='Helvetica-Oblique',
                alignment=TA_CENTER, spaceAfter=10)
    code_s  = S('cod', fontSize=8.5, textColor=BLUE, fontName='Courier',
                spaceAfter=4, leftIndent=12, backColor=colors.HexColor('#EFF6FF'))

    def sp(h=8): return Spacer(1, h)
    def hr(): return HRFlowable(width='100%', thickness=0.5,
                                color=colors.HexColor('#CBD5E1'), spaceAfter=6)

    def box_para(title, text, bg=TEAL2):
        data = [[Paragraph(f'<b>{title}</b>', ParagraphStyle('bt',fontSize=10,
                 textColor=TEAL,fontName='Helvetica-Bold')),
                 Paragraph(text, ParagraphStyle('bb',fontSize=9.5,
                 textColor=colors.HexColor('#1E3A30'),fontName='Helvetica',leading=14))]]
        t = Table(data, colWidths=[3.5*cm, 12*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 0.5, TEAL),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('ROUNDEDCORNERS', [4,4,4,4]),
        ]))
        return t

    def tbl(data, col_widths, header_color=NAVY):
        t = Table(data, colWidths=col_widths)
        style = [
            ('BACKGROUND', (0,0), (-1,0), header_color),
            ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,0), 9),
            ('ALIGN',      (0,0), (-1,0), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING',    (0,0), (-1,0), 8),
            ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',   (0,1), (-1,-1), 9),
            ('VALIGN',     (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING',    (0,1), (-1,-1), 6),
            ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
            ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0,i), (-1,i), GRAY))
        t.setStyle(TableStyle(style))
        return t

    def class_box(name, attrs, methods, w=15*cm):
        rows = []
        # Header
        rows.append([Paragraph(f'<b>«class» {name}</b>',
            ParagraphStyle('ch',fontSize=10,textColor=WHITE,fontName='Helvetica-Bold',
                           alignment=TA_CENTER))])
        # Attributes
        for a in attrs:
            rows.append([Paragraph(a, ParagraphStyle('ca',fontSize=8.5,
                textColor=colors.HexColor('#1E293B'),fontName='Courier'))])
        rows.append([''])  # divider row
        # Methods
        for m in methods:
            rows.append([Paragraph(m, ParagraphStyle('cm',fontSize=8.5,
                textColor=BLUE,fontName='Courier'))])

        t = Table(rows, colWidths=[w])
        style_list = [
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
            ('LEFTPADDING',  (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING',   (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ]
        # Color attribute rows
        for i in range(1, len(attrs)+1):
            style_list.append(('BACKGROUND', (0,i), (-1,i),
                               colors.HexColor('#F8FAFC')))
        # Divider row
        div_row = len(attrs)+1
        style_list.append(('BACKGROUND', (0,div_row),(-1,div_row),
                           colors.HexColor('#E2E8F0')))
        style_list.append(('TOPPADDING', (0,div_row),(-1,div_row), 2))
        style_list.append(('BOTTOMPADDING',(0,div_row),(-1,div_row), 2))
        # Method rows
        for i in range(div_row+1, len(rows)):
            style_list.append(('BACKGROUND',(0,i),(-1,i),WHITE))
        t.setStyle(TableStyle(style_list))
        return t

    def seq_row(step, frm, to, action, odd=True):
        bg = colors.HexColor('#F8FAFC') if odd else WHITE
        if step == '---':
            return [Paragraph(f'<b>{action}</b>',
                ParagraphStyle('sr',fontSize=9,textColor=colors.HexColor('#92400E'),
                               fontName='Helvetica-Bold',
                               backColor=colors.HexColor('#FEF3C7')))]
        return [Paragraph(
            f'<font color="#00A88A"><b>{step}.</b></font>  '
            f'<font color="#0A0F1E"><b>{frm} → {to}:</b></font>  '
            f'<font color="#475569">{action}</font>',
            ParagraphStyle('sr2',fontSize=9,fontName='Helvetica',
                           leading=13,backColor=bg))]

    story = []

    # ════════════════════════════════════════════════════════════
    # COVER PAGE
    # ════════════════════════════════════════════════════════════
    story += [
        sp(60),
        Paragraph('SkillLoop', cover_title),
        Paragraph('Global Student Skill Marketplace', cover_sub),
        sp(4),
        HRFlowable(width='60%', thickness=2, color=TEAL,
                   hAlign='CENTER', spaceAfter=20),
        sp(10),
        Paragraph('Software Architecture &amp; Design', cover_sub),
        Paragraph('Improvement Project Proposal', S('cp2',fontSize=14,
            textColor=MID,alignment=TA_CENTER,fontName='Helvetica')),
        sp(60),
        Paragraph('Prepared by: <b>Bushra Shaikh</b>', cover_info),
        Paragraph('Course: <b>Software &amp; Design Architecture</b>', cover_info),
        Paragraph('Academic Year: <b>2024–2025</b>', cover_info),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════
    # 1. INTRODUCTION
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('1. Introduction', h1_s), hr(),
        Paragraph(
            'SkillLoop is a web-based global student skill marketplace that enables '
            'university students worldwide to offer, discover, and exchange skills. '
            'Built using Python Flask as the backend, HTML/CSS/JavaScript for the '
            'frontend, and SQL Server as the database, SkillLoop provides a platform '
            'for students to monetise their academic and professional skills using a '
            'virtual currency called Campus Coins.', body),
        sp(6),
        Paragraph(
            'This report presents a comprehensive analysis of the SkillLoop system '
            'from a Software Architecture and Design perspective. It identifies '
            'architectural weaknesses in the initial design, proposes improvements '
            'using established GoF design patterns and architectural styles, and '
            'provides detailed UML diagrams including class diagrams, sequence '
            'diagrams, and component diagrams.', body),
        sp(8),
        box_para('Project Vision',
            'To create a globally accessible, scalable, and maintainable student '
            'skill marketplace that promotes peer-to-peer learning, skill exchange, '
            'and entrepreneurship within academic communities worldwide.'),
        sp(10),
        Paragraph('1.1 Project Scope', h2_s),
    ]
    scope_items = [
        'User registration with educational email verification (OTP-based system)',
        'Gig creation, browsing, filtering, and order placement system',
        'Real-time chat via Flask-SocketIO with Google Drive file sharing',
        'Campus Coins wallet with escrow system and Skill Swap payment alternative',
        'Project bidding marketplace for buyers to post and sellers to bid',
        'Role-based dashboard for Buyer, Seller, and Both roles (Factory Pattern)',
        'Admin panel for user management, gig moderation, and system analytics',
        'Event-driven notification system using Observer Pattern (DB + SocketIO + Email)',
    ]
    for item in scope_items:
        story.append(Paragraph(f'• {item}', bullet_s))
    story.append(sp(10))

    story.append(Paragraph('1.2 Technology Stack', h2_s))
    tech_data = [
        ['Component', 'Technology Used'],
        ['Backend Framework', 'Python Flask 3.0 with Blueprint architecture'],
        ['Database', 'SQL Server 2025 (SSMS) – 16 normalised tables'],
        ['Frontend', 'HTML5, CSS3, JavaScript with Jinja2 templates'],
        ['Real-time Communication', 'Flask-SocketIO with EventLet async mode'],
        ['Authentication', 'Flask-Login + Google OAuth (Adapter Pattern)'],
        ['Data Access Layer', 'pyodbc with context manager (raw SQL)'],
        ['Design Patterns', '5 GoF Patterns: Adapter, Factory, State, Strategy, Observer'],
        ['Security', 'Werkzeug password hashing, CSRF protection, OTP email verification'],
    ]
    story.append(tbl(tech_data, [5*cm, 10.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 2. BACKGROUND
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('2. Background', h1_s), hr(),
        Paragraph('2.1 Problem Statement', h2_s),
        Paragraph(
            'University students possess valuable skills in programming, graphic design, '
            'content writing, data science, and many other domains. However, no dedicated '
            'platform connects students specifically within academic communities with proper '
            'identity verification, a student-appropriate virtual currency system, and '
            'discovery algorithms that fairly promote both new and experienced talent.', body),
        sp(6),
        Paragraph(
            'Existing platforms such as Fiverr and Upwork are designed for professional '
            'markets and present significant barriers for students: professional payment '
            'gateways requiring bank accounts, no academic identity verification, and '
            'visibility algorithms that overwhelmingly favour established sellers with '
            'hundreds of reviews over new entrants.', body),
        sp(10),
        Paragraph('2.2 Before vs. After Architecture Comparison', h2_s),
    ]
    before_after = [
        ['Issue (Before Improvements)', 'Solution (After Improvements)'],
        ['No design patterns — duplicated code', '5 GoF patterns: Adapter, Factory, State, Strategy, Observer'],
        ['Monolithic controller logic', '10 Flask Blueprints with clean MVC separation'],
        ['Hardcoded payment logic in routes', 'Strategy Pattern — easily add new payment methods'],
        ['Direct DB calls inside route handlers', 'Model layer (DAO) via pyodbc context managers'],
        ['No notification abstraction', 'Observer Pattern with 3 pluggable observers'],
        ['No order state management', 'State Pattern — 6 states with enforced transitions'],
        ['Google OAuth tightly coupled', 'Adapter Pattern wrapping Google OAuth API'],
        ['Role setup hardcoded in auth route', 'Factory Pattern creating role-specific profiles'],
        ['No student verification system', 'OTP email verification with educational domain check'],
    ]
    story.append(tbl(before_after, [8*cm, 7.5*cm]))
    story.append(sp(10))

    story += [
        Paragraph('2.3 Related Work', h2_s),
        Paragraph('The proposed improvements are grounded in established software engineering principles:', body),
        Paragraph('• Gang of Four (GoF) Design Patterns — Gamma, Helm, Johnson, Vlissides (1994)', bullet_s),
        Paragraph('• Model-View-Controller (MVC) Architectural Pattern — Reenskaug (1979)', bullet_s),
        Paragraph('• SOLID Principles — Robert C. Martin (2000)', bullet_s),
        Paragraph('• RESTful API Design — Roy Fielding (2000)', bullet_s),
        Paragraph('• Event-Driven Architecture — for real-time notification systems', bullet_s),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════
    # 3. FUNCTIONAL REQUIREMENTS
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('3. Functional Requirements', h1_s), hr(),
        Paragraph('3.1 User Management', h2_s),
        Paragraph('• Only educational email addresses (.edu, .ac.pk, .edu.pk, .ac.uk, etc.) can register', bullet_s),
        Paragraph('• OTP email verification required before accessing any protected feature', bullet_s),
        Paragraph('• Google OAuth login supported via Adapter Pattern abstraction', bullet_s),
        Paragraph('• Role assignment (Buyer/Seller/Both) handled by Factory Pattern on profile setup', bullet_s),
        Paragraph('• User profiles include skills, bio, portfolio, university, country, and ratings', bullet_s),
        sp(6),
        Paragraph('3.2 Gig Management', h2_s),
        Paragraph('• Sellers create, edit, and deactivate gigs with categories, tags, and pricing', bullet_s),
        Paragraph('• Gigs support Campus Coins pricing and optional Skill Swap (no coins needed)', bullet_s),
        Paragraph('• Discovery algorithm fairly shows Top Performers, New Talent, and Rising Stars', bullet_s),
        Paragraph('• Buyers filter gigs by price range, minimum rating, delivery time, and university', bullet_s),
        sp(6),
        Paragraph('3.3 Order Management', h2_s),
        Paragraph('• Orders follow lifecycle: Pending → InProgress → Delivered → Completed', bullet_s),
        Paragraph('• State Pattern enforces valid transitions and blocks illegal state changes', bullet_s),
        Paragraph('• Strategy Pattern processes Campus Coins or Skill Swap payments identically', bullet_s),
        Paragraph('• Coins held in escrow until buyer explicitly approves delivery', bullet_s),
        Paragraph('• Buyers can approve, dispute, or cancel at appropriate lifecycle stages', bullet_s),
        sp(6),
        Paragraph('3.4 Communication &amp; Notifications', h2_s),
        Paragraph('• Real-time chat per order via Flask-SocketIO WebSocket connection', bullet_s),
        Paragraph('• File sharing via Google Drive links — no direct file upload to server', bullet_s),
        Paragraph('• Observer Pattern triggers DB storage, SocketIO push, and Email on all events', bullet_s),
        Paragraph('• Events: new order, new message, delivery, completion, bid placed, bid accepted', bullet_s),
        sp(6),
        Paragraph('3.5 Non-Functional Requirements', h2_s),
    ]
    nfr = [
        ['Requirement', 'Specification'],
        ['Performance',     'Page load under 2 seconds; DB queries with proper indexing'],
        ['Security',        'Password hashing (Werkzeug), OTP verification, role-based access control'],
        ['Usability',       'Responsive CSS design system for mobile and desktop'],
        ['Maintainability', 'MVC architecture, 5 design patterns, modular Flask Blueprints'],
        ['Scalability',     'Stateless controllers, connection pooling ready, Blueprint separation'],
        ['Reliability',     'Error handlers for 404, 403, 500; graceful DB connection fallbacks'],
        ['Verification',    'Educational email domain check + OTP verification flow'],
    ]
    story.append(tbl(nfr, [5*cm, 10.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 4. SYSTEM ARCHITECTURE DESIGN
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('4. System Architecture Design', h1_s), hr(),
        Paragraph('4a. Justification of Architectural Style', h2_s),
        Paragraph('Primary Style: Model-View-Controller (MVC)', h3_s),
        Paragraph(
            'SkillLoop adopts MVC as its primary architectural style. Flask\'s Blueprint '
            'system maps naturally to the Controller layer, Jinja2 templates form the View '
            'layer, and pyodbc-backed model classes form the Model layer. This three-tier '
            'separation ensures that changes to the user interface do not require changes '
            'to database logic, and vice versa.', body),
        sp(6),
    ]
    mvc_data = [
        ['MVC Layer', 'SkillLoop Implementation', 'Files/Components'],
        ['Model (M)', 'Domain model classes with DAO pattern',
         'app/models/ — 9 model classes'],
        ['View (V)', '34 Jinja2 HTML templates',
         'app/templates/ — 8 subfolders'],
        ['Controller (C)', '10 Flask Blueprint route handlers',
         'app/controllers/ — 10 blueprints'],
        ['Patterns', '5 GoF design pattern implementations',
         'app/patterns/ — 5 pattern files'],
        ['Utilities', 'DB connection + helper functions',
         'app/utils/ — db.py, helpers.py'],
    ]
    story.append(tbl(mvc_data, [3.5*cm, 6*cm, 6*cm]))
    story += [
        sp(10),
        Paragraph('Secondary Style: Event-Driven Architecture', h3_s),
        Paragraph(
            'The notification system uses Event-Driven Architecture through the Observer '
            'Pattern. Event producers (controllers) call NotificationPublisher.notify(event) '
            'without knowing about any consumer. Multiple consumers react independently: '
            'DatabaseObserver stores to SQL Server, SocketIOObserver pushes real-time, '
            'and EmailObserver sends critical-event emails.', body),
        sp(8),
        Paragraph('Layered Architecture — 5 Tiers', h3_s),
        Paragraph('• Layer 1 — Presentation: HTML/CSS/JS templates (Jinja2)', bullet_s),
        Paragraph('• Layer 2 — Controller: Flask Blueprints handling HTTP and WebSocket requests', bullet_s),
        Paragraph('• Layer 3 — Business Logic: 5 Design Patterns (Adapter, Factory, State, Strategy, Observer)', bullet_s),
        Paragraph('• Layer 4 — Data Access: pyodbc context managers with execute_query() abstraction', bullet_s),
        Paragraph('• Layer 5 — Database: SQL Server 2025 with 16 normalised tables', bullet_s),
        PageBreak(),
    ]

    # HIGH LEVEL ARCHITECTURE DIAGRAM (as table)
    story += [
        Paragraph('4b. High-Level Architectural Diagram', h2_s),
        Paragraph(
            'The following diagram represents the complete SkillLoop architecture '
            'across all 5 layers, showing components and their interactions:', body),
        sp(8),
    ]

    arch_layers = [
        [Paragraph('<b>PRESENTATION LAYER — Client Browser</b>',
            ParagraphStyle('al',fontSize=10,textColor=WHITE,fontName='Helvetica-Bold',
                           alignment=TA_CENTER))],
        [Paragraph('HTML5 + CSS3 Design System (34 templates) + JavaScript + SocketIO Client',
            ParagraphStyle('al2',fontSize=9,textColor=colors.HexColor('#94A3B8'),
                           fontName='Helvetica',alignment=TA_CENTER))],
        [Paragraph('↕  HTTP Requests / WebSocket (Flask-SocketIO)  ↕',
            ParagraphStyle('al3',fontSize=9,textColor=MID,fontName='Helvetica-Oblique',
                           alignment=TA_CENTER))],
        [Paragraph('<b>CONTROLLER LAYER — Flask Application (10 Blueprints)</b>',
            ParagraphStyle('al4',fontSize=10,textColor=WHITE,fontName='Helvetica-Bold',
                           alignment=TA_CENTER))],
        [Paragraph('main | auth | dashboard | gigs | orders | chat | wallet | projects | admin | profile',
            ParagraphStyle('al5',fontSize=8.5,textColor=colors.HexColor('#A7F3D0'),
                           fontName='Courier',alignment=TA_CENTER))],
        [Paragraph('↕  Method calls  ↕',
            ParagraphStyle('al6',fontSize=9,textColor=MID,fontName='Helvetica-Oblique',
                           alignment=TA_CENTER))],
    ]
    arch_colors = [
        colors.HexColor('#1E2A3A'),
        colors.HexColor('#162032'),
        WHITE,
        colors.HexColor('#0A4F3A'),
        colors.HexColor('#0D3A2E'),
        WHITE,
    ]
    arch_t = Table(arch_layers, colWidths=[15.5*cm])
    arch_style = [('LEFTPADDING',(0,0),(-1,-1),10),
                  ('RIGHTPADDING',(0,0),(-1,-1),10),
                  ('TOPPADDING',(0,0),(-1,-1),7),
                  ('BOTTOMPADDING',(0,0),(-1,-1),7),
                  ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#CBD5E1'))]
    for i,c in enumerate(arch_colors):
        arch_style.append(('BACKGROUND',(0,i),(-1,i),c))
    arch_t.setStyle(TableStyle(arch_style))
    story.append(arch_t)

    # Middle two columns
    mid_data = [[
        Paragraph('<b>BUSINESS LOGIC LAYER</b>\nDesign Patterns (app/patterns/)\n'
                  '• Adapter → Google OAuth\n• Factory → User Roles\n'
                  '• State → Order Lifecycle\n• Strategy → Payments\n'
                  '• Observer → Notifications',
            ParagraphStyle('ml',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
        Paragraph('<b>MODEL LAYER</b>\nDomain Models (app/models/)\n'
                  '• UserModel  GigModel\n• OrderModel  WalletModel\n'
                  '• MessageModel  ReviewModel\n• ProjectModel  BidModel\n'
                  '• NotificationModel',
            ParagraphStyle('mr',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
    ]]
    mid_t = Table(mid_data, colWidths=[7.75*cm, 7.75*cm])
    mid_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0),colors.HexColor('#1E3A5F')),
        ('BACKGROUND',(1,0),(1,0),colors.HexColor('#3B0764')),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#CBD5E1')),
        ('LINEAFTER',(0,0),(0,-1),0.5,colors.HexColor('#334155')),
    ]))
    story.append(mid_t)

    db_layers = [
        [Paragraph('<b>DATA ACCESS LAYER — app/utils/db.py (pyodbc context manager)</b>',
            ParagraphStyle('dl',fontSize=10,textColor=WHITE,fontName='Helvetica-Bold',alignment=TA_CENTER))],
        [Paragraph('<b>DATABASE LAYER — SQL Server 2025 | skillloop_db | 16 Tables</b>',
            ParagraphStyle('dl2',fontSize=10,textColor=TEAL,fontName='Helvetica-Bold',alignment=TA_CENTER))],
        [Paragraph('Users | Gigs | Orders | Wallet | Transactions | Messages | Reviews | '
                   'Projects | Bids | Notifications | Skills | UserSkills | Badges | GigImages | Portfolio | UserBadges',
            ParagraphStyle('dl3',fontSize=8,textColor=colors.HexColor('#94A3B8'),
                           fontName='Helvetica',alignment=TA_CENTER))],
    ]
    db_colors2 = [colors.HexColor('#1E293B'),colors.HexColor('#0F172A'),colors.HexColor('#162032')]
    db_t = Table(db_layers, colWidths=[15.5*cm])
    db_style = [('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
                ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
                ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#CBD5E1'))]
    for i,c in enumerate(db_colors2):
        db_style.append(('BACKGROUND',(0,i),(-1,i),c))
    db_t.setStyle(TableStyle(db_style))
    story.append(db_t)
    story += [
        sp(6),
        Paragraph('Figure 1: SkillLoop High-Level Architecture — 5-Layer Diagram', caption),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════
    # 4c. UML MODELLING
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('4c. UML Modelling', h2_s),
        Paragraph('Class Diagram — Core Domain Classes', h3_s),
        Paragraph(
            'The class diagram below shows the primary domain classes, their attributes, '
            'methods, and relationships in the SkillLoop system.', body),
        sp(8),
        class_box('User  (extends UserMixin)',
            ['+ user_id: int',
             '+ name: str',
             '+ email: str',
             '+ password_hash: str',
             '+ role: str   {buyer | seller | both | admin}',
             '+ university: str',
             '+ country: str',
             '+ is_verified: bool',
             '+ rating: float',
             '+ total_reviews: int'],
            ['+ check_password(password: str) → bool',
             '+ is_seller() → bool',
             '+ is_buyer() → bool',
             '+ is_admin() → bool',
             '+ get_id() → str (Flask-Login interface)']),
        sp(8),
    ]

    # Gig and Order side by side
    gig_t = class_box('GigModel',
        ['+ gig_id: int',
         '+ seller_id: int (FK → Users)',
         '+ title: str',
         '+ price: Decimal',
         '+ delivery_days: int',
         '+ allow_swap: bool',
         '+ rating: float',
         '+ orders_count: int'],
        ['+ get_featured(n: int) → list',
         '+ search(filters: dict) → list',
         '+ create(**kwargs) → int',
         '+ update_rating(gig_id: int) → void'],
        w=7.2*cm)

    order_t = class_box('OrderModel',
        ['+ order_id: int',
         '+ gig_id: int (FK → Gigs)',
         '+ buyer_id: int (FK → Users)',
         '+ seller_id: int (FK → Users)',
         '+ status: str',
         '+ payment_method: str',
         '+ amount: Decimal',
         '+ delivery_link: str'],
        ['+ create(**kwargs) → int',
         '+ update_status(s: str) → void',
         '+ get_by_buyer(id: int) → list',
         '+ get_seller_earnings(id) → float'],
        w=7.2*cm)

    row = Table([[gig_t, order_t]], colWidths=[7.7*cm, 7.7*cm])
    row.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('LEFTPADDING',(0,0),(-1,-1),0),
                              ('RIGHTPADDING',(0,0),(-1,-1),4)]))
    story.append(row)
    story.append(sp(8))

    wallet_t = class_box('WalletModel',
        ['+ wallet_id: int',
         '+ user_id: int (FK → Users)',
         '+ balance: Decimal',
         '+ updated_at: DateTime'],
        ['+ credit(uid, amt, desc) → void',
         '+ debit(uid, amt) → bool',
         '+ escrow(uid, amt, order_id) → void',
         '+ release_escrow(sid, amt, oid) → void'],
        w=7.2*cm)

    notif_t = class_box('NotificationModel',
        ['+ notif_id: int',
         '+ user_id: int (FK → Users)',
         '+ type: str',
         '+ title: str',
         '+ body: str',
         '+ is_read: bool'],
        ['+ create(uid, type, title) → int',
         '+ get_by_user(uid) → list',
         '+ mark_all_read(uid) → void',
         '+ unread_count(uid) → int'],
        w=7.2*cm)

    row2 = Table([[wallet_t, notif_t]], colWidths=[7.7*cm, 7.7*cm])
    row2.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                               ('LEFTPADDING',(0,0),(-1,-1),0),
                               ('RIGHTPADDING',(0,0),(-1,-1),4)]))
    story.append(row2)
    story += [sp(6), Paragraph('Figure 2: Core Domain Class Diagram', caption)]

    story += [
        sp(8),
        Paragraph('Class Relationships', h3_s),
    ]
    rel_data = [
        ['Relationship', 'Multiplicity', 'Description'],
        ['User → Gig',         '1 to many',  'A seller can create many gigs'],
        ['User → Order',       '1 to many',  'A buyer places many orders; a seller receives many'],
        ['Gig → Order',        '1 to many',  'Each order references exactly one gig'],
        ['Order → Review',     '1 to 0..1',  'Each completed order has one optional review'],
        ['Order → Message',    '1 to many',  'Each order has a chat thread with many messages'],
        ['User → Wallet',      '1 to 1',     'Each user has exactly one wallet (enforced by UNIQUE)'],
        ['Project → Bid',      '1 to many',  'Each buyer project receives many seller bids'],
        ['User ↔ Skill',       'many to many','Users have skills via UserSkills junction table'],
    ]
    story.append(tbl(rel_data, [4*cm, 3.5*cm, 8*cm]))
    story.append(PageBreak())

    # SEQUENCE DIAGRAMS
    story += [
        Paragraph('Sequence Diagram 1 — User Registration &amp; Verification', h3_s),
        Paragraph(
            'Shows the complete flow from signup through OTP email verification to '
            'dashboard access. Incorporates Factory Pattern for role assignment.', body),
        sp(6),
    ]
    seq1_data = [
        ['Participants: Browser → AuthController → UserModel → Database → EmailService'],
        ['1.  Browser → AuthController: POST /signup {name, email, password, university}'],
        ['2.  AuthController → AuthController: Validate — is_student_email(email)?'],
        ['3.  AuthController → AuthController: validate_password(password) — 8+ chars, uppercase, number'],
        ['4.  AuthController → UserModel: UserModel.get_by_email(email) — check for duplicates'],
        ['5.  UserModel → Database: SELECT FROM Users WHERE email = ?'],
        ['6.  AuthController → UserModel: UserModel.create(name, email, pw_hash, university)'],
        ['7.  UserModel → Database: INSERT INTO Users + INSERT INTO Wallet (balance=100)'],
        ['8.  AuthController → Browser: Redirect to /verify-student'],
        ['---STUDENT VERIFICATION FLOW---'],
        ['9.  Browser → AuthController: POST /verify-student {action: send_otp}'],
        ['10. AuthController → Database: Generate OTP, UPDATE Users SET otp_code, otp_expiry'],
        ['11. AuthController → EmailService: Send 6-digit code to user email'],
        ['12. Browser → AuthController: POST /verify-student {action: verify_otp, otp: 123456}'],
        ['13. AuthController → Database: SELECT otp_code, otp_expiry FROM Users WHERE user_id=?'],
        ['14. AuthController → AuthController: Validate — entered == stored AND now < expiry'],
        ['15. AuthController → UserModel: UserModel.verify_user(user_id, "otp")'],
        ['16. AuthController → Browser: Redirect to /profile-setup'],
        ['---PROFILE SETUP WITH FACTORY PATTERN---'],
        ['17. Browser → AuthController: POST /profile-setup {role, bio, skills}'],
        ['18. AuthController → UserFactory: UserFactory.create(user_id, role)  [Factory Pattern]'],
        ['19. UserFactory → Database: UPDATE Users SET role + credit initial coins + notify'],
        ['20. AuthController → Browser: Redirect to /dashboard'],
    ]
    seq1_rows = []
    for i, row in enumerate(seq1_data):
        t = row[0]
        if t.startswith('Participants'):
            bg = TEAL2
            tc = TEAL
        elif t.startswith('---'):
            bg = colors.HexColor('#FEF3C7')
            tc = colors.HexColor('#92400E')
        else:
            bg = GRAY if i % 2 == 0 else WHITE
            tc = colors.HexColor('#1E293B')
        seq1_rows.append([Paragraph(t, ParagraphStyle('sq',fontSize=8.5,
            fontName='Courier' if not t.startswith('---') else 'Helvetica-BoldOblique',
            textColor=tc, leading=12, backColor=bg))])

    seq1_t = Table(seq1_rows, colWidths=[15.5*cm])
    seq1_style = [('LEFTPADDING',(0,0),(-1,-1),8),
                  ('RIGHTPADDING',(0,0),(-1,-1),8),
                  ('TOPPADDING',(0,0),(-1,-1),4),
                  ('BOTTOMPADDING',(0,0),(-1,-1),4),
                  ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#CBD5E1'))]
    for i,row in enumerate(seq1_data):
        if row[0].startswith('Participants'):
            seq1_style.append(('BACKGROUND',(0,i),(-1,i),TEAL2))
        elif row[0].startswith('---'):
            seq1_style.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#FEF3C7')))
        elif i % 2 == 0:
            seq1_style.append(('BACKGROUND',(0,i),(-1,i),GRAY))
    seq1_t.setStyle(TableStyle(seq1_style))
    story.append(seq1_t)
    story += [
        sp(6),
        Paragraph('Figure 3: User Registration and Email OTP Verification Sequence Diagram', caption),
        PageBreak(),
    ]

    story += [
        Paragraph('Sequence Diagram 2 — Order Placement &amp; Completion', h3_s),
        Paragraph(
            'Shows the complete order lifecycle from placement to review, incorporating '
            'State Pattern (order transitions), Strategy Pattern (payments), and '
            'Observer Pattern (notifications).', body),
        sp(6),
    ]
    seq2_data = [
        ['Participants: Buyer → OrderController → PaymentContext → OrderContext → NotificationPublisher → Seller'],
        ['1.  Buyer → OrderController: POST /order/{gig_id} {payment_method, requirements}'],
        ['2.  OrderController → WalletModel: WalletModel.get_balance(buyer_id) — check coins'],
        ['3.  OrderController → PaymentContext: PaymentContext("coins").pay(buyer, seller, amount)  [Strategy]'],
        ['4.  PaymentContext → WalletModel: WalletModel.debit(buyer_id, amount) — deduct coins to escrow'],
        ['5.  OrderController → OrderModel: OrderModel.create(gig_id, buyer_id, seller_id, amount)'],
        ['6.  OrderController → OrderContext: OrderContext(order_id, "Pending").start_work()  [State]'],
        ['7.  OrderContext → OrderModel: OrderModel.update_status(order_id, "InProgress")'],
        ['8.  OrderController → NotificationPublisher: notify_new_order(buyer_name, seller_id)  [Observer]'],
        ['9.  NotificationPublisher → DatabaseObserver: NotificationModel.create(seller_id, "New Order")'],
        ['10. NotificationPublisher → SocketIOObserver: socketio.emit("notification", room="user_{seller_id}")'],
        ['11. OrderController → Buyer: Redirect to /chat/{order_id}'],
        ['---SELLER DELIVERS WORK---'],
        ['12. Seller → OrderController: POST /order-status/{id} {action: deliver, drive_link}'],
        ['13. OrderController → OrderContext: ctx.deliver(drive_link)  [State: InProgress → Delivered]'],
        ['14. OrderController → NotificationPublisher: notify_order_delivered(seller_name, buyer_id)  [Observer]'],
        ['---BUYER APPROVES DELIVERY---'],
        ['15. Buyer → OrderController: POST /order-status/{id} {action: approve}'],
        ['16. OrderController → OrderContext: ctx.approve()  [State: Delivered → Completed]'],
        ['17. OrderController → PaymentContext: PaymentContext("coins").release(seller_id, amount)  [Strategy]'],
        ['18. PaymentContext → WalletModel: WalletModel.credit(seller_id, amount) — release escrow'],
        ['19. OrderController → NotificationPublisher: notify_order_completed(buyer, seller, amount)  [Observer]'],
        ['20. OrderController → Buyer: Redirect to /review/{order_id}'],
    ]
    seq2_rows = []
    for i, row in enumerate(seq2_data):
        t = row[0]
        if t.startswith('Participants'):
            bg, tc = TEAL2, TEAL
        elif t.startswith('---'):
            bg, tc = colors.HexColor('#FEF3C7'), colors.HexColor('#92400E')
        else:
            bg = GRAY if i % 2 == 0 else WHITE
            tc = colors.HexColor('#1E293B')
        seq2_rows.append([Paragraph(t, ParagraphStyle('sq2',fontSize=8.5,
            fontName='Courier' if not t.startswith('---') else 'Helvetica-BoldOblique',
            textColor=tc,leading=12,backColor=bg))])

    seq2_t = Table(seq2_rows, colWidths=[15.5*cm])
    seq2_style = [('LEFTPADDING',(0,0),(-1,-1),8),
                  ('RIGHTPADDING',(0,0),(-1,-1),8),
                  ('TOPPADDING',(0,0),(-1,-1),4),
                  ('BOTTOMPADDING',(0,0),(-1,-1),4),
                  ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#CBD5E1'))]
    for i,row in enumerate(seq2_data):
        if row[0].startswith('Participants'):
            seq2_style.append(('BACKGROUND',(0,i),(-1,i),TEAL2))
        elif row[0].startswith('---'):
            seq2_style.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#FEF3C7')))
        elif i % 2 == 0:
            seq2_style.append(('BACKGROUND',(0,i),(-1,i),GRAY))
    seq2_t.setStyle(TableStyle(seq2_style))
    story.append(seq2_t)
    story += [
        sp(6),
        Paragraph('Figure 4: Order Lifecycle Sequence Diagram (State + Strategy + Observer patterns)', caption),
        PageBreak(),
    ]

    # COMPONENT DIAGRAM
    story += [
        Paragraph('Component Diagram', h3_s),
        Paragraph(
            'The component diagram shows how major architectural components interact '
            'with each other and with external systems.', body),
        sp(8),
    ]
    comp_data = [[
        Paragraph('<b>«component»\nFrontend Layer</b>\n\n'
                  '• Jinja2 Templates (34)\n• CSS Design System\n• JavaScript (SocketIO)',
            ParagraphStyle('cd1',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
        Paragraph('<b>«component»\nController Layer</b>\n\n'
                  '• 10 Flask Blueprints\n• Route handlers\n• Auth middleware\n• before_request hooks',
            ParagraphStyle('cd2',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
        Paragraph('<b>«component»\nDesign Patterns</b>\n\n'
                  '• Adapter (Google OAuth)\n• Factory (User Roles)\n• State (Orders)\n'
                  '• Strategy (Payments)\n• Observer (Notifications)',
            ParagraphStyle('cd3',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
    ],[
        Paragraph('<b>«component»\nModel Layer</b>\n\n'
                  '• UserModel\n• GigModel\n• OrderModel\n• WalletModel\n'
                  '• 5 more models',
            ParagraphStyle('cd4',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
        Paragraph('<b>«component»\nData Access</b>\n\n'
                  '• db.py context mgr\n• execute_query()\n• get_db_connection()\n• Error handling',
            ParagraphStyle('cd5',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
        Paragraph('<b>«external»\nExternal Services</b>\n\n'
                  '• Google OAuth API\n• Google Drive (links)\n• SMTP Email Server\n'
                  '• SQL Server 2025',
            ParagraphStyle('cd6',fontSize=9,textColor=WHITE,fontName='Helvetica',
                           alignment=TA_CENTER,leading=14)),
    ]]
    comp_t = Table(comp_data, colWidths=[5.1*cm, 5.1*cm, 5.1*cm])
    comp_colors = [
        [colors.HexColor('#1E40AF'),colors.HexColor('#065F46'),colors.HexColor('#78350F')],
        [colors.HexColor('#3B0764'),colors.HexColor('#1E293B'),colors.HexColor('#164E63')],
    ]
    cs = [('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
          ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
          ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#334155')),
          ('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor('#334155')),
          ('VALIGN',(0,0),(-1,-1),'TOP')]
    for r,row_colors in enumerate(comp_colors):
        for c,col_color in enumerate(row_colors):
            cs.append(('BACKGROUND',(c,r),(c,r),col_color))
    comp_t.setStyle(TableStyle(cs))
    story.append(comp_t)
    story += [
        sp(6),
        Paragraph('Figure 5: SkillLoop Component Diagram', caption),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════
    # 4d. DESIGN PATTERNS
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('4d. Design Patterns with Justification', h2_s),
    ]

    # ── ADAPTER ──────────────────────────────────────────────────
    story += [
        Paragraph('Pattern 1: Adapter Pattern — Google Authentication', h3_s),
        box_para('Classification','Category: Structural | GoF | File: app/patterns/google_auth_adapter.py'),
        sp(6),
        Paragraph('<b>Problem:</b> Google OAuth returns user data in Google-specific format '
                  '(sub, email_verified, hd). Every controller handling login must know these '
                  'field names. Adding GitHub or LinkedIn later requires changing every auth-related '
                  'controller.', body),
        Paragraph('<b>Solution:</b> The GoogleAuthAdapter wraps GoogleOAuthClient (the Adaptee) and '
                  'translates its response into a standard dict {provider_id, email, name, '
                  'is_verified} that the rest of the application understands. The Target Interface '
                  'AuthProviderInterface defines get_auth_url(), exchange_code(), get_user_info().', body),
        sp(6),
    ]
    adapter_data = [
        ['Target Interface', 'Adaptee (External)', 'Adapter'],
        ['AuthProviderInterface\n+ get_auth_url()\n+ exchange_code()\n+ get_user_info()\n→ returns normalised dict',
         'GoogleOAuthClient\n+ build_auth_url()\n+ fetch_token()\n+ fetch_userinfo()\n→ returns {sub, email_verified, hd…}',
         'GoogleAuthAdapter\n  implements AuthProviderInterface\n  wraps GoogleOAuthClient\n→ translates to {provider_id,\n   email, name, is_verified}'],
    ]
    story.append(tbl(adapter_data, [4.5*cm, 5.5*cm, 5.5*cm]))
    story += [
        sp(6),
        Paragraph('<b>Justification:</b> To add LinkedIn authentication, only create '
                  'LinkedInAuthAdapter implementing AuthProviderInterface. Zero changes '
                  'to controllers or auth routes.', body),
        sp(10),
    ]

    # ── FACTORY ──────────────────────────────────────────────────
    story += [
        Paragraph('Pattern 2: Factory Pattern — User Role Creation', h3_s),
        box_para('Classification','Category: Creational | GoF | File: app/patterns/user_factory.py'),
        sp(6),
        Paragraph('<b>Problem:</b> Creating a user with role "buyer", "seller", or "both" '
                  'requires different setup: different permissions, initial coins, dashboard '
                  'tabs, badges, and welcome messages. Hardcoding this in the profile setup '
                  'controller creates a long if/elif chain.', body),
        Paragraph('<b>Solution:</b> UserFactory.create(user_id, role) selects the appropriate '
                  'concrete creator (BuyerCreator, SellerCreator, BothCreator) and returns a '
                  'UserProfile object with complete role-specific configuration.', body),
        sp(6),
    ]
    factory_data = [
        ['Factory', 'BuyerCreator', 'SellerCreator', 'BothCreator'],
        ['UserFactory\n.create(id, role)\n→ UserProfile',
         'coins: 100\nperms: browse,\n order, review\nbadge: New Buyer',
         'coins: 50\nperms: create_gig,\n deliver,\n analytics\nbadge: New Talent',
         'coins: 100\nperms: ALL\n(buyer + seller)\nbadges: both'],
    ]
    story.append(tbl(factory_data, [3.5*cm, 4*cm, 4*cm, 4*cm]))
    story += [
        sp(6),
        Paragraph('<b>Justification:</b> Adding an "institution" role requires only creating '
                  'InstitutionCreator class. The controller calls UserFactory.create() '
                  'identically — open for extension, closed for modification (Open/Closed Principle).', body),
        sp(10),
    ]

    # ── STATE ────────────────────────────────────────────────────
    story += [
        Paragraph('Pattern 3: State Pattern — Order Lifecycle', h3_s),
        box_para('Classification','Category: Behavioural | GoF | File: app/patterns/order_state.py'),
        sp(6),
        Paragraph('<b>Problem:</b> An order transitions through 6 states. Each state allows '
                  'different actions. Using if/else chains in controllers becomes a maintenance '
                  'nightmare as the system grows.', body),
        Paragraph('<b>Solution:</b> Each state is a class implementing OrderState interface. '
                  'OrderContext delegates all actions to current state. Illegal transitions '
                  'return descriptive error messages.', body),
        sp(6),
    ]
    state_data = [
        ['State', 'Allowed Actions', 'Blocked Actions', 'Terminal?'],
        ['Pending',    'start_work(), cancel()',          'deliver(), approve(), dispute()', 'No'],
        ['InProgress', 'deliver(), cancel(), dispute()',  'start_work(), approve()',         'No'],
        ['Delivered',  'approve(), dispute(), redeliver()','cancel(), start_work()',         'No'],
        ['Completed',  'none',                             'ALL blocked',                    'YES ✓'],
        ['Cancelled',  'none',                             'ALL blocked',                    'YES ✓'],
        ['Disputed',   'approve(), cancel() (admin only)', 'start_work(), deliver()',        'No'],
    ]
    story.append(tbl(state_data, [2.5*cm, 4.5*cm, 5*cm, 3*cm]))
    story += [
        sp(6),
        Paragraph('<b>Justification:</b> Adding a "Revision Requested" state requires only '
                  'creating RevisionState class. OrderContext.start_work() etc. remain '
                  'unchanged — state-specific logic is fully encapsulated.', body),
        sp(10),
    ]

    # ── STRATEGY ─────────────────────────────────────────────────
    story += [
        Paragraph('Pattern 4: Strategy Pattern — Payment Processing', h3_s),
        box_para('Classification','Category: Behavioural | GoF | File: app/patterns/payment_strategy.py'),
        sp(6),
        Paragraph('<b>Problem:</b> SkillLoop supports Campus Coins and Skill Swap payments. '
                  'The order controller must not contain if/else logic for payment types, '
                  'as this violates Open/Closed Principle when adding PayPal or Stripe.', body),
        Paragraph('<b>Solution:</b> PaymentStrategy interface defines pay(), refund(), release(). '
                  'PaymentContext selects the correct strategy at runtime. Controllers call '
                  'PaymentContext("coins").pay(...) regardless of method.', body),
        sp(6),
    ]
    strategy_data = [
        ['Method', 'CampusCoinsStrategy', 'SkillSwapStrategy'],
        ['pay()',     'Debit buyer wallet; record escrow transaction',     'Record swap agreement; no coins deducted'],
        ['release()', 'Credit seller wallet; record release transaction', 'Mark swap complete; no coin movement'],
        ['refund()',  'Credit buyer wallet on cancellation',              'No action — no coins were held'],
    ]
    story.append(tbl(strategy_data, [2.5*cm, 6.5*cm, 6.5*cm]))
    story += [
        sp(6),
        Paragraph('<b>Justification:</b> Adding Stripe payments requires only creating '
                  'StripeStrategy. PaymentContext("stripe") selects it automatically. '
                  'All controllers remain unchanged.', body),
        sp(10),
    ]

    # ── OBSERVER ─────────────────────────────────────────────────
    story += [
        Paragraph('Pattern 5: Observer Pattern — Notification System', h3_s),
        box_para('Classification','Category: Behavioural | GoF | File: app/patterns/notification_observer.py'),
        sp(6),
        Paragraph('<b>Problem:</b> Events (new order, message, delivery, completion, bid) must '
                  'trigger DB storage, real-time push, and email. Without Observer Pattern, '
                  'every controller calls all three services directly — creating tight coupling.', body),
        Paragraph('<b>Solution:</b> NotificationPublisher maintains a list of observers. When an '
                  'event occurs, the controller calls NotificationPublisher.notify(event). All '
                  'registered observers react automatically and independently.', body),
        sp(6),
    ]
    observer_data = [
        ['Observer', 'Triggers On', 'Action'],
        ['DatabaseNotificationObserver', 'ALL events',
         'Calls NotificationModel.create() — stores to SQL Server Notifications table'],
        ['SocketIONotificationObserver', 'ALL events',
         'socketio.emit("notification", payload) to user_{id} room'],
        ['EmailNotificationObserver',    'Critical events only\n(order_placed, completed, disputed)',
         'Sends email via Flask-Mail SMTP integration'],
    ]
    story.append(tbl(observer_data, [4*cm, 3.5*cm, 8*cm]))
    story += [
        sp(6),
        Paragraph('<b>Justification:</b> Adding SMS notifications requires only implementing '
                  'NotificationObserver and calling NotificationPublisher.subscribe(SMSObserver()). '
                  'Zero changes to any controller or existing observer.', body),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════
    # 5. PROPOSED IMPROVEMENTS
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('5. Proposed Improvements for Future Development', h1_s), hr(),
        Paragraph('5.1 Architectural Improvements', h2_s),
    ]
    improve_data = [
        ['Improvement', 'Benefit', 'Priority'],
        ['Add Service Layer (app/services/)',  'Separate business logic from controllers', 'High'],
        ['Implement Repository Pattern',       'Abstract DB queries behind interfaces',    'High'],
        ['Add API Blueprint (/api/v1/)',        'Enable mobile app integrations',           'Medium'],
        ['Implement Caching (Redis)',           'Reduce DB load for featured gigs',         'Medium'],
        ['Async task queue (Celery + Redis)',   'Handle email/heavy ops asynchronously',    'Medium'],
        ['Containerise with Docker',           'Consistent deployment environments',        'Low'],
        ['Database migration tool (Alembic)',  'Version-controlled schema changes',         'High'],
    ]
    story.append(tbl(improve_data, [5*cm, 6.5*cm, 3.5*cm]))
    story += [
        sp(10),
        Paragraph('5.2 Additional Design Patterns', h2_s),
    ]
    pattern_improve = [
        ['Design Pattern', 'Proposed Use Case', 'Benefit'],
        ['Decorator Pattern', 'Add permission checks to routes without modifying controller logic', 'Clean access control'],
        ['Command Pattern',   'Undo functionality for admin actions (deactivate user, remove gig)',  'Reversibility'],
        ['Template Method',   'Standardise order processing steps across payment types',              'Consistency'],
        ['Facade Pattern',    'Simplify external service integrations (email, OAuth, storage)',        'Simplicity'],
        ['Repository Pattern','Abstract all database queries behind clean interface classes',          'Testability'],
    ]
    story.append(tbl(pattern_improve, [4*cm, 7*cm, 4.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # 6. CONCLUSION
    # ════════════════════════════════════════════════════════════
    story += [
        Paragraph('6. Conclusion', h1_s), hr(),
        Paragraph(
            'SkillLoop demonstrates a comprehensive application of software architecture '
            'principles in a real-world student marketplace context. The system successfully '
            'implements the MVC architectural pattern across 10 Flask Blueprints, 9 domain '
            'model classes, 34 HTML templates, and 5 GoF design patterns.', body),
        sp(6),
        Paragraph(
            'The five GoF design patterns applied collectively address the core quality '
            'attributes of the system. The Adapter Pattern enables authentication provider '
            'independence. The Factory Pattern encapsulates role-specific initialisation. '
            'The State Pattern enforces valid order lifecycle transitions. The Strategy '
            'Pattern enables payment method extensibility. The Observer Pattern decouples '
            'event producers from notification consumers.', body),
        sp(6),
        Paragraph(
            'The proposed improvements — Service Layer, Repository Pattern, API Blueprint, '
            'and caching — provide a clear roadmap for evolving the system toward a '
            'production-ready, scalable platform suitable for mobile applications and '
            'third-party integrations.', body),
        sp(10),
        box_para('Key Achievement',
            'SkillLoop applies 5 GoF patterns, MVC architecture, a 16-table SQL Server schema, '
            'real-time SocketIO communication, Google OAuth via Adapter Pattern, OTP email '
            'verification, Campus Coins escrow system, and role-based access control — all '
            'within a coherent, layered Flask application demonstrating standardised, '
            'reusable, and readable software architecture.'),
    ]

    doc.build(story)
    print('Report PDF created!')

build_report()