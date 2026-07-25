from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

W, H = landscape(A4)

NAVY    = colors.HexColor('#0A0F1E')
NAVY2   = colors.HexColor('#1E2A3A')
TEAL    = colors.HexColor('#00C9A7')
TEAL2   = colors.HexColor('#00A88A')
TEAL_BG = colors.HexColor('#E1F5EE')
WHITE   = colors.white
GRAY    = colors.HexColor('#F1F5F9')
MID     = colors.HexColor('#64748B')
RED     = colors.HexColor('#EF4444')
BLUE    = colors.HexColor('#1E40AF')
MARGIN  = 1.2*cm

def build_presentation():
    doc = SimpleDocTemplate(
        r'C:\Users\Bushra Shaikh\Desktop\SkillLoop_Presentation.pdf',
        pagesize=landscape(A4),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title='SkillLoop - Architecture Presentation',
        author='Bushra Shaikh'
    )

    def S(name, **kw): return ParagraphStyle(name, **kw)
    def sp(h=6): return Spacer(1, h)

    def color_to_hex(c):
        return '#{:02X}{:02X}{:02X}'.format(
            int(c.red*255), int(c.green*255), int(c.blue*255))

    def slide_header(title, subtitle=None, accent=TEAL, bg=NAVY):
        title_p = Paragraph(
            f'<font color="{color_to_hex(accent)}">{title}</font>',
            S('sh', fontSize=22, textColor=WHITE,
              fontName='Helvetica-Bold', alignment=TA_LEFT, leading=26))
        rows = [[title_p]]
        if subtitle:
            rows.append([Paragraph(subtitle,
                S('ss', fontSize=12, textColor=colors.HexColor('#94A3B8'),
                  fontName='Helvetica', alignment=TA_LEFT))])
        t = Table(rows, colWidths=[27*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), bg),
            ('LEFTPADDING',(0,0),(-1,-1), 16),
            ('RIGHTPADDING',(0,0),(-1,-1), 16),
            ('TOPPADDING',(0,0),(-1,-1), 10),
            ('BOTTOMPADDING',(0,0),(-1,-1), 10),
        ]))
        return t

    def card(title, items, bg=TEAL_BG, title_color=TEAL2, w=8.5*cm):
        data = [[Paragraph(title, S('ct', fontSize=11, textColor=title_color,
                    fontName='Helvetica-Bold'))]]
        for item in items:
            data.append([Paragraph(f'* {item}', S('ci', fontSize=9.5,
                textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=13))])
        t = Table(data, colWidths=[w - 0.4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), bg),
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor('#B2F0E0')),
            ('LEFTPADDING',(0,0),(-1,-1), 10),
            ('RIGHTPADDING',(0,0),(-1,-1), 10),
            ('TOPPADDING',(0,0),(-1,-1), 7),
            ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('BOX',(0,0),(-1,-1), 0.5, colors.HexColor('#A7D7C5')),
        ]))
        return t

    def dark_card(title, items, bg=NAVY2, w=8.5*cm):
        data = [[Paragraph(title, S('dct', fontSize=11, textColor=TEAL,
                    fontName='Helvetica-Bold'))]]
        for item in items:
            data.append([Paragraph(f'* {item}', S('dci', fontSize=9.5,
                textColor=colors.HexColor('#CBD5E1'), fontName='Helvetica', leading=13))])
        t = Table(data, colWidths=[w - 0.4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), bg),
            ('LEFTPADDING',(0,0),(-1,-1), 10),
            ('RIGHTPADDING',(0,0),(-1,-1), 10),
            ('TOPPADDING',(0,0),(-1,-1), 7),
            ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('BOX',(0,0),(-1,-1), 0.5, colors.HexColor('#334155')),
        ]))
        return t

    def tbl2(data, widths, hdr_color=NAVY):
        t = Table(data, colWidths=widths)
        style = [
            ('BACKGROUND',(0,0),(-1,0), hdr_color),
            ('TEXTCOLOR',(0,0),(-1,0), WHITE),
            ('FONTNAME',(0,0),(-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,0), 9),
            ('ALIGN',(0,0),(-1,0), 'CENTER'),
            ('TOPPADDING',(0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('LEFTPADDING',(0,0),(-1,-1), 8),
            ('RIGHTPADDING',(0,0),(-1,-1), 8),
            ('FONTNAME',(0,1),(-1,-1), 'Helvetica'),
            ('FONTSIZE',(0,1),(-1,-1), 9),
            ('GRID',(0,0),(-1,-1), 0.4, colors.HexColor('#CBD5E1')),
            ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND',(0,i),(-1,i), GRAY))
        t.setStyle(TableStyle(style))
        return t

    def compare_row(before, after):
        t = Table([[
            Paragraph(f'X  {before}', S('br', fontSize=9,
                textColor=colors.HexColor('#991B1B'), fontName='Helvetica', leading=13)),
            Paragraph('->', S('arr', fontSize=14, textColor=MID,
                fontName='Helvetica', alignment=TA_CENTER)),
            Paragraph(f'OK  {after}', S('ar', fontSize=9,
                textColor=colors.HexColor('#166534'), fontName='Helvetica', leading=13)),
        ]], colWidths=[11.5*cm, 1.5*cm, 11.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,0), colors.HexColor('#FEF2F2')),
            ('BACKGROUND',(2,0),(2,0), colors.HexColor('#F0FDF4')),
            ('BOX',(0,0),(0,0), 0.5, colors.HexColor('#FECACA')),
            ('BOX',(2,0),(2,0), 0.5, colors.HexColor('#BBF7D0')),
            ('LEFTPADDING',(0,0),(-1,-1), 8),
            ('TOPPADDING',(0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
        ]))
        return t

    story = []

    # SLIDE 1 - COVER
    cover = Table([
        [Paragraph('SkillLoop', S('cv', fontSize=52, textColor=WHITE,
            fontName='Helvetica-Bold', alignment=TA_CENTER))],
        [Paragraph('Global Student Skill Marketplace', S('cvs', fontSize=18,
            textColor=TEAL, fontName='Helvetica', alignment=TA_CENTER))],
        [sp(8)],
        [HRFlowable(width='40%', thickness=2, color=TEAL, hAlign='CENTER')],
        [sp(8)],
        [Paragraph('Software Architecture &amp; Design', S('cvt', fontSize=14,
            textColor=colors.HexColor('#94A3B8'), fontName='Helvetica-Bold',
            alignment=TA_CENTER))],
        [Paragraph('Improvement Project Proposal - Before &amp; After',
            S('cvt2', fontSize=12, textColor=MID, fontName='Helvetica',
            alignment=TA_CENTER))],
        [sp(20)],
        [Paragraph('Bushra Shaikh  |  Software &amp; Design Architecture  |  2024-2025',
            S('cva', fontSize=11, textColor=MID, fontName='Helvetica',
            alignment=TA_CENTER))],
    ], colWidths=[27*cm])
    cover.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), NAVY),
        ('TOPPADDING',(0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
    ]))
    story += [cover, PageBreak()]

    # SLIDE 2 - AGENDA
    story.append(slide_header('Presentation Agenda', 'What we will cover today'))
    story.append(sp(12))

    agenda_items = [
        ('01', 'Introduction',            'What is SkillLoop? Vision, scope, technology stack'),
        ('02', 'Background',              'Problem statement and before vs. after comparison'),
        ('03', 'Functional Requirements', 'User management, gigs, orders, notifications'),
        ('04', 'System Architecture',     'MVC + Layered + Event-Driven architectural styles'),
        ('05', 'UML Diagrams',            'Class diagram, sequence diagrams, component diagram'),
        ('06', 'Design Patterns',         'Adapter, Factory, State, Strategy, Observer'),
        ('07', 'Proposed Improvements',   'Future enhancements for scalability'),
        ('08', 'Conclusion',              'Key achievements and architectural value'),
    ]
    agenda_rows = [[
        Paragraph(num, S('an', fontSize=16, textColor=TEAL,
            fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph(f'<b>{title}</b>', S('at', fontSize=11, textColor=NAVY,
            fontName='Helvetica-Bold')),
        Paragraph(desc, S('ad', fontSize=9.5, textColor=MID, fontName='Helvetica')),
    ] for num, title, desc in agenda_items]
    agenda_t = Table(agenda_rows, colWidths=[1.5*cm, 5.5*cm, 20*cm])
    agenda_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING',(0,0),(-1,-1), 8),
        ('LINEBEFORE',(1,0),(1,-1), 2, TEAL),
        ('LINEBELOW',(0,0),(-1,-1), 0.3, colors.HexColor('#E2E8F0')),
    ]))
    story += [agenda_t, PageBreak()]

    # SLIDE 3 - INTRODUCTION
    story.append(slide_header('01  Introduction', 'What is SkillLoop?'))
    story.append(sp(10))

    left_data = [
        [Paragraph('What is SkillLoop?', S('il', fontSize=13, textColor=NAVY,
            fontName='Helvetica-Bold'))],
        [Paragraph('A web-based global student skill marketplace that connects '
            'university students worldwide to offer, discover, and exchange '
            'skills using Campus Coins — a virtual currency designed for '
            'academic communities.',
            S('ib', fontSize=10, textColor=colors.HexColor('#334155'),
              fontName='Helvetica', leading=15))],
        [Paragraph('Core Features', S('il2', fontSize=11, textColor=TEAL2,
            fontName='Helvetica-Bold'))],
        [Paragraph('* Student identity verification (OTP)', S('f1', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
        [Paragraph('* Gig marketplace with filters', S('f2', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
        [Paragraph('* Real-time chat via WebSocket', S('f3', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
        [Paragraph('* Campus Coins + Skill Swap payments', S('f4', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
        [Paragraph('* Project bidding system', S('f5', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
        [Paragraph('* Role-based dashboards', S('f6', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
        [Paragraph('* Admin panel', S('f7', fontSize=9.5,
            textColor=colors.HexColor('#1E293B'), fontName='Helvetica', leading=14))],
    ]
    left_t = Table(left_data, colWidths=[11*cm])
    left_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1), 0),
        ('RIGHTPADDING',(0,0),(-1,-1), 4),
        ('TOPPADDING',(0,0),(-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ]))

    tech = [
        ('Backend',   'Python Flask 3.0'),
        ('Database',  'SQL Server 2025'),
        ('Frontend',  'HTML5 + CSS3 + JS'),
        ('Real-time', 'Flask-SocketIO'),
        ('Auth',      'Flask-Login + OAuth'),
        ('Patterns',  '5 GoF Patterns'),
        ('Tables',    '16 SQL Tables'),
        ('Templates', '34 HTML Templates'),
    ]
    tech_data = [
        [Paragraph('Technology Stack', S('ir', fontSize=11,
            textColor=WHITE, fontName='Helvetica-Bold')),
         Paragraph('', S('ir_b', fontSize=9, fontName='Helvetica'))]
    ]
    for label, val in tech:
        tech_data.append([
            Paragraph(label, S(f'tl_{label}', fontSize=9,
                textColor=colors.HexColor('#94A3B8'), fontName='Helvetica')),
            Paragraph(f'<b>{val}</b>', S(f'tv_{label}', fontSize=9,
                textColor=WHITE, fontName='Helvetica-Bold')),
        ])
    tech_t = Table(tech_data, colWidths=[4*cm, 10*cm])
    tech_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), NAVY),
        ('BACKGROUND',(0,1),(-1,-1), NAVY2),
        ('SPAN',(0,0),(1,0)),
        ('TOPPADDING',(0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING',(0,0),(-1,-1), 8),
        ('RIGHTPADDING',(0,0),(-1,-1), 8),
        ('LINEBELOW',(0,1),(-1,-1), 0.3, colors.HexColor('#334155')),
        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
    ]))

    two_col = Table([[left_t, tech_t]], colWidths=[11.5*cm, 14.5*cm])
    two_col.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1), 0),
        ('RIGHTPADDING',(0,0),(-1,-1), 0),
        ('TOPPADDING',(0,0),(-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0),
    ]))
    story += [two_col, PageBreak()]

    # SLIDE 4 - BEFORE vs AFTER
    story.append(slide_header('02  Background',
        'System before vs. after architectural improvements'))
    story.append(sp(8))

    comparisons = [
        ('No design patterns — duplicated code everywhere',
         '5 GoF patterns: Adapter, Factory, State, Strategy, Observer'),
        ('Monolithic controller with all logic mixed together',
         '10 Flask Blueprints with clean MVC layer separation'),
        ('Hardcoded payment if/else logic in order routes',
         'Strategy Pattern — add Stripe/PayPal without changing controllers'),
        ('Direct DB calls inside Flask route handlers',
         'Model layer (DAO) with pyodbc context manager abstraction'),
        ('No notification abstraction — tightly coupled calls',
         'Observer Pattern with 3 independent, pluggable observers'),
        ('No order state management — inconsistent transitions',
         'State Pattern — 6 states, enforced transitions, illegal actions blocked'),
        ('Google OAuth tightly coupled to auth controller',
         'Adapter Pattern — add GitHub/LinkedIn with zero controller changes'),
        ('No student verification — anyone could sign up',
         'OTP email verification + educational domain (.edu) enforcement'),
    ]
    for b, a in comparisons:
        story.append(compare_row(b, a))
        story.append(sp(3))
    story.append(PageBreak())

    # SLIDE 5 - FUNCTIONAL REQUIREMENTS
    story.append(slide_header('03  Functional Requirements', ''))
    story.append(sp(10))
    req_data = [
        ['Area', 'Key Requirements'],
        ['User Management',  'Edu-only signup (.edu/.ac.pk) - OTP verification - Google OAuth - Role Factory'],
        ['Gig Marketplace',  'Create/edit/deactivate gigs - Coin + Swap pricing - Fair discovery algorithm'],
        ['Order System',     'Pending to InProgress to Delivered to Completed - State Pattern - Coins escrow'],
        ['Payments',         'Strategy Pattern: CampusCoinsStrategy - SkillSwapStrategy - Escrow + Release'],
        ['Communication',    'Real-time WebSocket chat - Google Drive file sharing - Notification Observer'],
        ['Bidding',          'Post projects with budget - Place bids - Accept bid creates order automatically'],
        ['Admin Panel',      'Manage users (deactivate) - Manage gigs (remove) - View orders - Analytics'],
        ['Non-Functional',   'Responsive UI - Password hashing - CSRF - Role-based access - Error handlers'],
    ]
    story.append(tbl2(req_data, [4*cm, 23*cm]))
    story.append(PageBreak())

    # SLIDE 6 - ARCHITECTURE OVERVIEW
    story.append(slide_header('04  System Architecture Design',
        'MVC + Layered + Event-Driven architectural styles'))
    story.append(sp(8))
    story.append(Paragraph(
        '<b>Primary Style: MVC</b> — Clean separation of Models (9 classes), '
        'Views (34 templates), Controllers (10 Blueprints). '
        '<b>Secondary: Event-Driven</b> — Observer Pattern for notifications. '
        '<b>Tertiary: Layered</b> — 5 distinct tiers from presentation to database.',
        S('at', fontSize=10, textColor=colors.HexColor('#1E293B'),
          fontName='Helvetica', leading=15)))
    story.append(sp(8))

    layers = [
        (colors.HexColor('#1E2A3A'), WHITE,
         'LAYER 1 — PRESENTATION',
         'HTML5 + CSS3 Design System (34 Jinja2 templates) + JavaScript + SocketIO Client'),
        (colors.HexColor('#0A4F3A'), WHITE,
         'LAYER 2 — CONTROLLER',
         '10 Flask Blueprints: main | auth | dashboard | gigs | orders | chat | wallet | projects | admin | profile'),
        (colors.HexColor('#1E3A5F'), WHITE,
         'LAYER 3 — BUSINESS LOGIC',
         'Patterns: Adapter (Google Auth) - Factory (Roles) - State (Orders) - Strategy (Payments) - Observer (Notifications)'),
        (colors.HexColor('#3B0764'), WHITE,
         'LAYER 4 — MODEL / DATA ACCESS',
         'UserModel - GigModel - OrderModel - WalletModel - MessageModel - ReviewModel - ProjectModel - BidModel'),
        (colors.HexColor('#0F172A'), TEAL,
         'LAYER 5 — DATABASE',
         'SQL Server 2025 | skillloop_db | 16 normalised tables with foreign key constraints'),
    ]
    for bg, tc, lyr_title, desc in layers:
        lt = Table([[
            Paragraph(lyr_title, S('lt', fontSize=10, textColor=tc, fontName='Helvetica-Bold')),
            Paragraph(desc, S('ld', fontSize=9, textColor=colors.HexColor('#94A3B8'), fontName='Helvetica')),
        ]], colWidths=[6*cm, 21*cm])
        lt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), bg),
            ('TOPPADDING',(0,0),(-1,-1), 7),
            ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('LEFTPADDING',(0,0),(-1,-1), 12),
            ('RIGHTPADDING',(0,0),(-1,-1), 12),
            ('LINEBEFORE',(0,0),(0,-1), 3, TEAL),
            ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
        ]))
        story.append(lt)
        story.append(sp(2))
    story.append(PageBreak())

    # SLIDE 7 - UML CLASS DIAGRAM
    story.append(slide_header('05  UML — Class Diagram', 'Core domain classes and relationships'))
    story.append(sp(8))

    def mini_class(name, attrs, methods, w=6.5*cm, hdr=NAVY):
        cw = w - 0.4*cm
        rows = [[Paragraph(f'class {name}', S('mc', fontSize=9, textColor=WHITE,
                    fontName='Helvetica-Bold', alignment=TA_CENTER))]]
        for a in attrs:
            rows.append([Paragraph(a, S('ma', fontSize=8, fontName='Courier',
                textColor=colors.HexColor('#334155')))])
        rows.append([Paragraph('- - - - - - - -', S('div', fontSize=7,
            textColor=colors.HexColor('#CBD5E1')))])
        for m in methods:
            rows.append([Paragraph(m, S('mm', fontSize=8, fontName='Courier',
                textColor=BLUE))])
        t = Table(rows, colWidths=[cw])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), hdr),
            ('BACKGROUND',(0,1),(-1,len(attrs)), colors.HexColor('#F8FAFC')),
            ('BACKGROUND',(0,len(attrs)+1),(-1,len(attrs)+1), colors.HexColor('#E2E8F0')),
            ('BACKGROUND',(0,len(attrs)+2),(-1,-1), colors.HexColor('#EFF6FF')),
            ('GRID',(0,0),(-1,-1), 0.3, colors.HexColor('#CBD5E1')),
            ('TOPPADDING',(0,0),(-1,-1), 3),
            ('BOTTOMPADDING',(0,0),(-1,-1), 3),
            ('LEFTPADDING',(0,0),(-1,-1), 6),
            ('RIGHTPADDING',(0,0),(-1,-1), 6),
        ]))
        return t

    user_c   = mini_class('User (UserMixin)',
        ['+ user_id: int','+ name: str','+ email: str',
         '+ role: str','+ is_verified: bool','+ rating: float'],
        ['+ check_password() bool','+ is_seller() bool',
         '+ is_buyer() bool','+ get_id() str'])
    gig_c    = mini_class('GigModel',
        ['+ gig_id: int','+ seller_id: int','+ price: Decimal',
         '+ allow_swap: bool','+ rating: float'],
        ['+ get_featured() list','+ search() list','+ create() int'])
    order_c  = mini_class('OrderModel',
        ['+ order_id: int','+ status: str','+ amount: Decimal',
         '+ payment_method: str','+ delivery_link: str'],
        ['+ create() int','+ update_status() void','+ get_by_buyer() list'])
    wallet_c = mini_class('WalletModel',
        ['+ wallet_id: int','+ user_id: int','+ balance: Decimal'],
        ['+ credit() void','+ debit() bool',
         '+ escrow() void','+ release_escrow() void'])

    classes_t = Table([[user_c, gig_c, order_c, wallet_c]],
        colWidths=[6.7*cm, 6.7*cm, 6.7*cm, 6.7*cm])
    classes_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1), 2),
        ('RIGHTPADDING',(0,0),(-1,-1), 2),
    ]))
    story.append(classes_t)
    story.append(sp(8))

    rel_data = [
        ['Relationship', 'Multiplicity', 'Description'],
        ['User to Gig',     '1..*', 'A seller creates many gigs'],
        ['User to Order',   '1..*', 'A buyer places / seller receives many orders'],
        ['Gig to Order',    '1..*', 'Each order references exactly one gig'],
        ['Order to Review', '0..1', 'One optional review per completed order'],
        ['User to Wallet',  '1..1', 'Each user has exactly one wallet'],
        ['Project to Bid',  '1..*', 'Each buyer project receives many seller bids'],
    ]
    story.append(tbl2(rel_data, [5*cm, 3*cm, 19*cm]))
    story.append(PageBreak())

    # SLIDE 8 - SEQUENCE DIAGRAM 1
    story.append(slide_header('05  UML — Sequence Diagram 1',
        'User Registration - OTP Verification - Profile Setup (Factory Pattern)'))
    story.append(sp(8))
    seq1 = [
        ('Browser',        'AuthController', 'POST /signup {name, email, password, university}'),
        ('AuthController', 'AuthController', 'Validate: is_student_email() + validate_password()'),
        ('AuthController', 'UserModel',      'UserModel.create(name, email, pw_hash, university)'),
        ('UserModel',      'Database',       'INSERT INTO Users + INSERT INTO Wallet (balance=100)'),
        ('AuthController', 'Browser',        'Redirect to /verify-student'),
        ('Browser',        'AuthController', 'POST /verify-student {action: send_otp}'),
        ('AuthController', 'Database',       'UPDATE Users SET otp_code=123456, otp_expiry=+10min'),
        ('AuthController', 'EmailService',   'Send 6-digit code to user@university.edu.pk'),
        ('Browser',        'AuthController', 'POST /verify-student {action: verify_otp, otp: 123456}'),
        ('AuthController', 'AuthController', 'Validate: entered==stored AND now < expiry'),
        ('AuthController', 'UserModel',      'UserModel.verify_user(user_id, otp)'),
        ('AuthController', 'Browser',        'Redirect to /profile-setup'),
        ('Browser',        'AuthController', 'POST /profile-setup {role: seller, bio, skills}'),
        ('AuthController', 'UserFactory',    'UserFactory.create(user_id, seller)  [Factory Pattern]'),
        ('UserFactory',    'Database',       'UPDATE role + credit coins + create welcome notification'),
        ('AuthController', 'Browser',        'Redirect to /dashboard'),
    ]
    seq_rows = [['Step', 'From', 'To', 'Message / Action']]
    for i, (frm, to, msg) in enumerate(seq1, 1):
        seq_rows.append([str(i), frm, to, msg])
    story.append(tbl2(seq_rows, [1.2*cm, 4*cm, 4*cm, 17.8*cm]))
    story.append(PageBreak())

    # SLIDE 9 - SEQUENCE DIAGRAM 2
    story.append(slide_header('05  UML — Sequence Diagram 2',
        'Order Placement - Delivery - Approval (State + Strategy + Observer)'))
    story.append(sp(8))
    seq2 = [
        ('Buyer',                 'OrderController',       'POST /order/{gig_id} {payment_method: coins}'),
        ('OrderController',       'WalletModel',           'get_balance(buyer_id) — verify sufficient coins'),
        ('OrderController',       'PaymentContext',        'PaymentContext(coins).pay(buyer, seller, 50) [Strategy]'),
        ('PaymentContext',         'WalletModel',           'WalletModel.debit(buyer_id, 50) — escrow coins'),
        ('OrderController',       'OrderModel',            'OrderModel.create(gig_id, buyer_id, seller_id, 50)'),
        ('OrderController',       'OrderContext',          'OrderContext(id, Pending).start_work() [State]'),
        ('OrderContext',           'OrderModel',            'update_status(order_id, InProgress)'),
        ('OrderController',       'NotificationPublisher', 'notify_new_order() [Observer Pattern]'),
        ('NotificationPublisher', 'DatabaseObserver',      'NotificationModel.create(seller_id, New Order)'),
        ('NotificationPublisher', 'SocketIOObserver',      'emit(notification) to user_{seller_id} room'),
        ('OrderController',       'Buyer',                 'Redirect to /chat/{order_id}'),
        ('Seller',                'OrderController',       'POST /order-status/{id} {action: deliver}'),
        ('OrderController',       'OrderContext',          'ctx.deliver() [State: InProgress to Delivered]'),
        ('OrderController',       'NotificationPublisher', 'notify_order_delivered() - Buyer notified'),
        ('Buyer',                 'OrderController',       'POST /order-status/{id} {action: approve}'),
        ('OrderController',       'OrderContext',          'ctx.approve() [State: Delivered to Completed]'),
        ('OrderController',       'PaymentContext',        'PaymentContext.release(seller_id, 50) [Strategy]'),
        ('PaymentContext',         'WalletModel',           'WalletModel.credit(seller_id, 50) — release escrow'),
        ('OrderController',       'NotificationPublisher', 'notify_order_completed() — coins released'),
        ('OrderController',       'Buyer',                 'Redirect to /review/{order_id}'),
    ]
    seq2_rows = [['Step', 'From', 'To', 'Message / Action']]
    for i, (frm, to, msg) in enumerate(seq2, 1):
        seq2_rows.append([str(i), frm, to, msg])
    story.append(tbl2(seq2_rows, [1.2*cm, 4.5*cm, 4.5*cm, 16.8*cm]))
    story.append(PageBreak())

    # SLIDE 10 - COMPONENT DIAGRAM
    story.append(slide_header('05  UML — Component Diagram',
        'How all architectural components interact'))
    story.append(sp(8))
    comp_t = Table([
        [
            dark_card('component: Frontend Layer',
                ['34 Jinja2 Templates','CSS Design System','JavaScript','SocketIO Client'], w=8.5*cm),
            dark_card('component: Controller Layer',
                ['10 Flask Blueprints','Route handlers','Auth middleware','before_request hooks'],
                bg=colors.HexColor('#1E3A5F'), w=8.5*cm),
            dark_card('component: Design Patterns',
                ['Adapter (Google Auth)','Factory (User Roles)','State (Order Lifecycle)',
                 'Strategy (Payments)','Observer (Notifications)'],
                bg=colors.HexColor('#78350F'), w=8.5*cm),
        ],[
            dark_card('component: Model Layer',
                ['UserModel','GigModel','OrderModel','WalletModel',
                 'MessageModel','ProjectModel','NotificationModel'],
                bg=colors.HexColor('#3B0764'), w=8.5*cm),
            dark_card('component: Data Access Layer',
                ['db.py context manager','execute_query()','get_db_connection()','Connection pooling'],
                bg=colors.HexColor('#1E293B'), w=8.5*cm),
            dark_card('external: External Services',
                ['Google OAuth API','Google Drive (links)','SMTP Email Server','SQL Server 2025'],
                bg=colors.HexColor('#164E63'), w=8.5*cm),
        ]
    ], colWidths=[9*cm, 9*cm, 9*cm])
    comp_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ('TOPPADDING',(0,0),(-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ('LEFTPADDING',(0,0),(-1,-1), 3),
        ('RIGHTPADDING',(0,0),(-1,-1), 3),
    ]))
    story.append(comp_t)
    story.append(PageBreak())

    # SLIDE 11 - DESIGN PATTERNS OVERVIEW
    story.append(slide_header('06  Design Patterns',
        '5 GoF patterns applied — rationale and justification'))
    story.append(sp(8))
    patterns = [
        ('01', colors.HexColor('#1E40AF'), 'Adapter Pattern',  'Structural',
         'Google OAuth returns {sub, email_verified}. App needs {provider_id, email, name}.',
         'Adding GitHub login = create GitHubAuthAdapter. Zero controller changes.'),
        ('02', colors.HexColor('#065F46'), 'Factory Pattern',  'Creational',
         'Buyer/Seller/Both setup requires different permissions, coins, tabs, badges.',
         'Adding new role = create new Creator class. Open/Closed Principle satisfied.'),
        ('03', colors.HexColor('#92400E'), 'State Pattern',    'Behavioural',
         'Orders have 6 states. Each allows different actions. if/else chains unmaintainable.',
         'Each state is a class. Illegal transitions auto-blocked. New state = new class.'),
        ('04', colors.HexColor('#7C3AED'), 'Strategy Pattern', 'Behavioural',
         'Campus Coins and Skill Swap need different pay/refund/release logic.',
         'Adding Stripe = create StripeStrategy. Controllers unchanged. DRY principle.'),
        ('05', colors.HexColor('#991B1B'), 'Observer Pattern', 'Behavioural',
         'Events must trigger DB save, SocketIO push, and email independently.',
         'Adding SMS = create SMSObserver. subscribe() it. Zero other changes.'),
    ]
    pat_rows = [['#', 'Pattern', 'Category', 'Problem Solved', 'Justification / Benefit']]
    for num, clr, name, cat, problem, justify in patterns:
        pat_rows.append([num, name, cat, problem, justify])
    pat_t = Table(pat_rows, colWidths=[1*cm, 4*cm, 3*cm, 10*cm, 10*cm])
    pat_style = [
        ('BACKGROUND',(0,0),(-1,0), NAVY),
        ('TEXTCOLOR',(0,0),(-1,0), WHITE),
        ('FONTNAME',(0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0), 9),
        ('ALIGN',(0,0),(-1,0), 'CENTER'),
        ('GRID',(0,0),(-1,-1), 0.3, colors.HexColor('#CBD5E1')),
        ('FONTNAME',(0,1),(-1,-1), 'Helvetica'),
        ('FONTSIZE',(0,1),(-1,-1), 9),
        ('TOPPADDING',(0,0),(-1,-1), 7),
        ('BOTTOMPADDING',(0,0),(-1,-1), 7),
        ('LEFTPADDING',(0,0),(-1,-1), 7),
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
    ]
    for i, (_, clr, *__) in enumerate(patterns, 1):
        pat_style += [
            ('BACKGROUND',(0,i),(0,i), clr),
            ('TEXTCOLOR',(0,i),(0,i), WHITE),
            ('FONTNAME',(0,i),(0,i), 'Helvetica-Bold'),
        ]
    pat_t.setStyle(TableStyle(pat_style))
    story.append(pat_t)
    story.append(PageBreak())

    # SLIDE 12 - ADAPTER PATTERN DETAIL
    story.append(slide_header('06  Pattern Detail — Adapter Pattern',
        'Google OAuth abstraction using structural design pattern'))
    story.append(sp(8))
    before_t = Table([
        [Paragraph('Without Adapter (BEFORE)', S('bef', fontSize=11,
            textColor=RED, fontName='Helvetica-Bold'))],
        [Paragraph('* Auth controller directly calls Google API\n'
            '* Uses raw Google field names: sub, email_verified, hd\n'
            '* Adding GitHub requires modifying auth controller\n'
            '* Tightly coupled to one provider\n'
            '* Violates Single Responsibility Principle',
            S('bul', fontSize=9.5, textColor=colors.HexColor('#1E293B'),
              fontName='Helvetica', leading=15))],
    ], colWidths=[12.5*cm])
    after_t = Table([
        [Paragraph('With Adapter (AFTER)', S('aft', fontSize=11,
            textColor=TEAL2, fontName='Helvetica-Bold'))],
        [Paragraph('* AuthProviderInterface defines standard contract\n'
            '* GoogleAuthAdapter translates {sub} to {provider_id}\n'
            '* Controller only knows AuthProviderInterface\n'
            '* Add LinkedIn: create LinkedInAuthAdapter\n'
            '* Zero changes to controllers or tests',
            S('bul2', fontSize=9.5, textColor=colors.HexColor('#1E293B'),
              fontName='Helvetica', leading=15))],
    ], colWidths=[12.5*cm])
    adapter_t = Table([[before_t, after_t]], colWidths=[13*cm, 14*cm])
    adapter_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1), 0),
        ('RIGHTPADDING',(0,0),(-1,-1), 0),
    ]))
    story.append(adapter_t)
    story.append(sp(10))
    flow_data = [['AuthController','->','AuthProviderInterface','->',
                  'GoogleAuthAdapter','->','GoogleOAuthClient (Adaptee)']]
    flow_t = Table(flow_data, colWidths=[4*cm,1*cm,5*cm,1*cm,5*cm,1*cm,10*cm])
    fc = [colors.HexColor('#1E40AF'),WHITE,colors.HexColor('#065F46'),WHITE,
          colors.HexColor('#0A4F3A'),WHITE,colors.HexColor('#1E293B')]
    fst = [('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),10),
           ('BOTTOMPADDING',(0,0),(-1,-1),10),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
           ('FONTSIZE',(0,0),(-1,0),9),('ALIGN',(0,0),(-1,0),'CENTER')]
    for i, c in enumerate(fc):
        fst.append(('BACKGROUND',(i,0),(i,0), c))
        fst.append(('TEXTCOLOR',(i,0),(i,0), WHITE if c != WHITE else MID))
    flow_t.setStyle(TableStyle(fst))
    story.append(flow_t)
    story.append(PageBreak())

    # SLIDE 13 - STATE PATTERN DETAIL
    story.append(slide_header('06  Pattern Detail — State Pattern',
        'Order lifecycle with enforced state transitions'))
    story.append(sp(8))
    state_data = [[
        Paragraph('Pending',     S('s1', fontSize=10, textColor=WHITE,
            fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph('->', S('ar1', fontSize=14, textColor=MID,
            fontName='Helvetica', alignment=TA_CENTER)),
        Paragraph('InProgress',  S('s2', fontSize=10, textColor=WHITE,
            fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph('->', S('ar2', fontSize=14, textColor=MID,
            fontName='Helvetica', alignment=TA_CENTER)),
        Paragraph('Delivered',   S('s3', fontSize=10, textColor=WHITE,
            fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph('->', S('ar3', fontSize=14, textColor=MID,
            fontName='Helvetica', alignment=TA_CENTER)),
        Paragraph('Completed', S('s4', fontSize=10, textColor=WHITE,
            fontName='Helvetica-Bold', alignment=TA_CENTER)),
    ]]
    state_t = Table(state_data, colWidths=[4.5*cm,1*cm,4.5*cm,1*cm,4.5*cm,1*cm,4.5*cm])
    sc = [colors.HexColor('#78350F'),None,colors.HexColor('#1E40AF'),None,
          colors.HexColor('#065F46'),None,colors.HexColor('#14532D')]
    sst = [('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),12),
           ('BOTTOMPADDING',(0,0),(-1,-1),12),('ALIGN',(0,0),(-1,-1),'CENTER')]
    for i, c in enumerate(sc):
        if c: sst.append(('BACKGROUND',(i,0),(i,0), c))
    state_t.setStyle(TableStyle(sst))
    story.append(state_t)
    story.append(sp(8))
    state_tbl = [
        ['State',      'Allowed Actions',                  'Blocked',                       'Terminal?'],
        ['Pending',    'start_work()  cancel()',            'deliver()  approve()  dispute()', 'No'],
        ['InProgress', 'deliver()  cancel()  dispute()',   'start_work()  approve()',         'No'],
        ['Delivered',  'approve()  redeliver()  dispute()','cancel()  start_work()',          'No'],
        ['Completed',  'none',                             'ALL actions blocked',             'YES'],
        ['Cancelled',  'none',                             'ALL actions blocked',             'YES'],
        ['Disputed',   'approve()  cancel() (admin)',      'start_work()  deliver()',         'No'],
    ]
    story.append(tbl2(state_tbl, [3.5*cm, 6*cm, 8*cm, 3*cm]))
    story.append(PageBreak())

    # SLIDE 14 - OBSERVER PATTERN DETAIL
    story.append(slide_header('06  Pattern Detail — Observer Pattern',
        'Event-driven notification system with 3 independent observers'))
    story.append(sp(8))
    obs_t = Table([[
        dark_card('Event Producer (Controllers)',
            ['notify_new_order()','notify_new_message()','notify_order_delivered()',
             'notify_order_completed()','notify_new_bid()','notify_bid_accepted()'],
            bg=NAVY2, w=8.5*cm),
        dark_card('NotificationPublisher (Subject)',
            ['subscribe(observer)','unsubscribe(observer)','notify(event)',
             'get_observer_names()','Maintains observer list'],
            bg=colors.HexColor('#1E3A5F'), w=8.5*cm),
        dark_card('3 Concrete Observers',
            ['DatabaseObserver: saves to SQL Server',
             'SocketIOObserver: real-time push to browser',
             'EmailObserver: critical events only',
             'Adding SMS: just create SMSObserver'],
            bg=colors.HexColor('#3B0764'), w=8.5*cm),
    ]], colWidths=[9*cm, 9*cm, 9*cm])
    obs_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),3),
    ]))
    story.append(obs_t)
    story.append(sp(8))
    events_data = [
        ['Event Type',     'DatabaseObserver', 'SocketIOObserver',  'EmailObserver'],
        ['order_placed',   'Save to DB',        'Push to seller',    'Email (critical)'],
        ['message_sent',   'Save to DB',        'Push to user',      'Not sent'],
        ['order_delivered','Save to DB',        'Push to buyer',     'Not sent'],
        ['order_completed','Save to DB',        'Push to seller',    'Email (critical)'],
        ['bid_placed',     'Save to DB',        'Push to buyer',     'Not sent'],
        ['dispute_raised', 'Save to DB',        'Push to both',      'Email (critical)'],
    ]
    story.append(tbl2(events_data, [4.5*cm, 5.5*cm, 5.5*cm, 5.5*cm]))
    story.append(PageBreak())

    # SLIDE 15 - PROPOSED IMPROVEMENTS
    story.append(slide_header('07  Proposed Improvements',
        'Future architectural enhancements for scalability'))
    story.append(sp(10))
    impr_t = Table([[
        card('High Priority', [
            'Service Layer (app/services/)',
            'Repository Pattern for DB abstraction',
            'Database migration tool (Alembic)',
            'Unit + integration test suite (pytest)',
            'Type hints on all model methods',
        ], w=9*cm),
        card('Medium Priority', [
            'REST API Blueprint (/api/v1/)',
            'Redis caching for featured gigs',
            'Async task queue (Celery)',
            'Decorator Pattern for permissions',
            'Command Pattern for undo actions',
        ], w=9*cm),
        card('Lower Priority', [
            'Docker containerisation',
            'Template Method for order processing',
            'Facade Pattern for external services',
            'CI/CD pipeline (GitHub Actions)',
            'Horizontal scaling with load balancer',
        ], w=9*cm),
    ]], colWidths=[9.1*cm, 9.1*cm, 9.1*cm])
    impr_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),3),
    ]))
    story.append(impr_t)
    story.append(sp(10))
    add_pat = [
        ['Pattern',    'Proposed Use Case',                                      'SOLID Principle'],
        ['Decorator',  'Add permission checks to routes without modifying them', 'Open/Closed'],
        ['Command',    'Implement undo for admin actions (deactivate, remove)',   'Single Responsibility'],
        ['Repository', 'Abstract all DB queries behind a clean interface',       'Dependency Inversion'],
        ['Facade',     'Simplify Google OAuth, email, and Drive API calls',      'Single Responsibility'],
    ]
    story.append(tbl2(add_pat, [5*cm, 13*cm, 5*cm]))
    story.append(PageBreak())

    # SLIDE 16 - CONCLUSION
    story.append(slide_header('08  Conclusion', 'Key achievements and architectural value'))
    story.append(sp(10))
    ach_t = Table([[
        dark_card('Architecture Applied',
            ['MVC across 10 Flask Blueprints','9 model classes (DAO pattern)',
             '34 HTML templates (View layer)','5-layer architecture',
             '16-table SQL Server schema'], w=9*cm),
        dark_card('Patterns Applied',
            ['Adapter — OAuth independence','Factory — Role encapsulation',
             'State — Order lifecycle','Strategy — Payment extensibility',
             'Observer — Event decoupling'],
            bg=colors.HexColor('#1E3A5F'), w=9*cm),
        dark_card('Quality Attributes',
            ['Maintainability: MVC separation','Extensibility: 5 GoF patterns',
             'Testability: Layered architecture','Reusability: Pattern abstractions',
             'Security: OTP + hashing + RBAC'],
            bg=colors.HexColor('#3B0764'), w=9*cm),
    ]], colWidths=[9.1*cm, 9.1*cm, 9.1*cm])
    ach_t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),3),
    ]))
    story.append(ach_t)
    story.append(sp(10))
    rat_t = Table([[Paragraph(
        '<b>Architectural Rationale:</b>  SkillLoop\'s before-state had zero design '
        'pattern application, monolithic controllers, and tightly coupled code. The '
        'after-state applies 5 GoF patterns that each solve a concrete problem: '
        'Adapter removes OAuth coupling, Factory encapsulates role creation, State '
        'enforces order transitions, Strategy enables payment flexibility, and '
        'Observer decouples notification channels. Every pattern follows the '
        'Open/Closed Principle — the system can be extended without modifying '
        'existing classes. This makes SkillLoop maintainable, testable, and ready '
        'for future growth into a production-ready, globally scaled platform.',
        S('rat', fontSize=10, textColor=colors.HexColor('#1E293B'),
          fontName='Helvetica', leading=16))
    ]], colWidths=[27*cm])
    rat_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), TEAL_BG),
        ('LEFTPADDING',(0,0),(-1,-1), 14),
        ('RIGHTPADDING',(0,0),(-1,-1), 14),
        ('TOPPADDING',(0,0),(-1,-1), 12),
        ('BOTTOMPADDING',(0,0),(-1,-1), 12),
        ('BOX',(0,0),(-1,-1), 1.5, TEAL2),
    ]))
    story.append(rat_t)
    story.append(PageBreak())

    # SLIDE 17 - THANK YOU
    thanks = Table([
        [Paragraph('Thank You', S('ty', fontSize=48, textColor=WHITE,
            fontName='Helvetica-Bold', alignment=TA_CENTER))],
        [sp(6)],
        [HRFlowable(width='30%', thickness=2, color=TEAL, hAlign='CENTER')],
        [sp(6)],
        [Paragraph('Questions &amp; Discussion', S('tys', fontSize=18, textColor=TEAL,
            fontName='Helvetica', alignment=TA_CENTER))],
        [sp(20)],
        [Paragraph('SkillLoop — Global Student Skill Marketplace',
            S('typ', fontSize=12, textColor=MID, fontName='Helvetica', alignment=TA_CENTER))],
        [Paragraph('Software Architecture &amp; Design  |  Bushra Shaikh  |  2024-2025',
            S('typ2', fontSize=11, textColor=colors.HexColor('#475569'),
            fontName='Helvetica', alignment=TA_CENTER))],
        [sp(16)],
        [Paragraph('Architecture: MVC + Layered + Event-Driven  |  '
            'Patterns: Adapter - Factory - State - Strategy - Observer',
            S('tyf', fontSize=10, textColor=colors.HexColor('#334155'),
            fontName='Helvetica', alignment=TA_CENTER))],
    ], colWidths=[27*cm])
    thanks.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), NAVY),
        ('TOPPADDING',(0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
    ]))
    story.append(thanks)

    doc.build(story)
    print('Presentation PDF created successfully!')

build_presentation()