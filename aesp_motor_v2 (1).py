# ══════════════════════════════════════════════════════════════════════
# AESP BOLETÍN EJECUTIVO — MOTOR v2.0
# Archivo estático. NO modificar salvo cambios de diseño estructural.
# Uso: python3 aesp_motor_v2.py noticias_HOY.json [output.pdf]
# ══════════════════════════════════════════════════════════════════════
import json, sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable

# ── PALETA ────────────────────────────────────────────────────────────
BG_PAGE   = colors.HexColor('#eceef0')
BG_HEADER = colors.HexColor('#1a2332')
BG_DARK   = colors.HexColor('#232d3a')
BG_STRIP  = colors.HexColor('#d8dde3')
BG_CARD   = colors.HexColor('#f2f4f6')
BG_CARD2  = colors.white
NEGRO     = colors.HexColor('#0d1117')
GRIS_OSC  = colors.HexColor('#263040')
GRIS_MED  = colors.HexColor('#445566')
GRIS_CL   = colors.HexColor('#667788')
GRIS_LN   = colors.HexColor('#b0bcc8')
DORADO    = colors.HexColor('#c4961e')
DORADO_CL = colors.HexColor('#e0b840')
DORADO_OSC= colors.HexColor('#8a6810')
DORADO_BG = colors.HexColor('#faf5e4')
PLAT_BG   = colors.HexColor('#d8e2ec')
PLAT_CL   = colors.HexColor('#9aacbc')
PLATEADO  = colors.HexColor('#7890a4')
ROJO      = colors.HexColor('#a81818')
ROJO_CL   = colors.HexColor('#cc2222')
ROJO_BG   = colors.HexColor('#fdf0f0')
AZUL      = colors.HexColor('#16407a')
AZUL_CL   = colors.HexColor('#2255a0')
AZUL_BG   = colors.HexColor('#eaf2fd')
VERDE     = colors.HexColor('#145c28')
VERDE_BG  = colors.HexColor('#eaf5ee')
AMBAR     = colors.HexColor('#8a5800')
AMBAR_BG  = colors.HexColor('#fdf4e0')
NARANJA   = colors.HexColor('#a84800')
NARANJA_BG= colors.HexColor('#fdf2ea')
PURPURA   = colors.HexColor('#4a1890')
PURPURA_BG= colors.HexColor('#f2eaff')
ACERO     = colors.HexColor('#3a4a5a')
ACERO_BG  = colors.HexColor('#eef0f4')
BLANCO    = colors.white
W, H = letter
CW = W - 2*inch

# ── MAPAS DE COLOR ────────────────────────────────────────────────────
CMAP = {
    'red':'rojo','alert':ROJO,'rojo':ROJO,'verde':VERDE,'green':VERDE,
    'ambar':AMBAR,'yellow':AMBAR,'azul':AZUL,'blue':AZUL,
    'dorado':DORADO_OSC,'gold':DORADO_OSC,'purpura':PURPURA,'purple':PURPURA,
    'leg':AZUL,'eco':VERDE,'binacional':PURPURA,'highlight':DORADO_OSC,
    'acero':ACERO,'naranja':NARANJA,'plateado':PLATEADO,
}
CMAP['red']=ROJO
BGMAP = {
    'red':ROJO_BG,'alert':ROJO_BG,'rojo':ROJO_BG,'verde':VERDE_BG,'green':VERDE_BG,
    'ambar':AMBAR_BG,'yellow':AMBAR_BG,'azul':AZUL_BG,'blue':AZUL_BG,
    'eco':VERDE_BG,'leg':AZUL_BG,'binacional':PURPURA_BG,'purpura':PURPURA_BG,
    'highlight':DORADO_BG,'dorado':DORADO_BG,'acero':ACERO_BG,'naranja':NARANJA_BG,
}
ACCENT_MAP = {
    'dorado':DORADO,'rojo':ROJO,'azul':AZUL,'verde':VERDE,
    'ambar':AMBAR,'purpura':PURPURA,'acero':ACERO,'plateado':PLATEADO,
    'naranja':NARANJA,
}

# ── CÍRCULO ────────────────────────────────────────────────────────────
class CircleFl(Flowable):
    def __init__(self, color, size=10):
        self.color=color; self.size=size
        self.width=size; self.height=size
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.circle(self.size/2,self.size/2,self.size/2,fill=1,stroke=0)

# ── ESTILOS ────────────────────────────────────────────────────────────
def _S(name,**kw):
    base=dict(fontName='Helvetica',fontSize=8,leading=11,textColor=NEGRO,
              spaceAfter=0,spaceBefore=0)
    return ParagraphStyle(name,**{**base,**kw})

ST={
    'edition':  _S('ed',fontSize=7,textColor=DORADO_CL,fontName='Helvetica-Bold',alignment=TA_CENTER),
    'date_sub': _S('ds',fontSize=6.5,textColor=PLAT_CL,alignment=TA_CENTER),
    'masthead': _S('mh',fontSize=17,textColor=DORADO,fontName='Helvetica-Bold',alignment=TA_CENTER,spaceAfter=2),
    'tagline':  _S('tl',fontSize=7,textColor=BLANCO,alignment=TA_CENTER),
    'dest_label':_S('dl',fontSize=6,textColor=DORADO_OSC,fontName='Helvetica-Bold'),
    'dest_name': _S('dn',fontSize=9,textColor=NEGRO,fontName='Helvetica-Bold'),
    'dest_cargo':_S('dc',fontSize=7,textColor=GRIS_MED),
    'sec_hdr':  _S('sh',fontSize=9.5,textColor=NEGRO,fontName='Helvetica-Bold',spaceAfter=1),
    'sec_label':_S('sl',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold',spaceAfter=2),
    'stat_val': _S('sv',fontSize=20,textColor=NEGRO,fontName='Helvetica-Bold',alignment=TA_CENTER,leading=22),
    'stat_lbl': _S('slb',fontSize=6.5,textColor=GRIS_MED,alignment=TA_CENTER,leading=8),
    'source':   _S('src',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold',spaceAfter=1),
    'headline': _S('hl',fontSize=9,textColor=NEGRO,fontName='Helvetica-Bold',leading=12,spaceAfter=3),
    'body':     _S('bd',fontSize=8,textColor=GRIS_OSC,leading=11,alignment=TA_JUSTIFY,spaceAfter=3),
    'link':     _S('lk',fontSize=6.5,textColor=AZUL_CL,leading=9),
    'voz_name': _S('vn',fontSize=10,textColor=NEGRO,fontName='Helvetica-Bold',spaceAfter=3),
    'voz_body': _S('vb',fontSize=8.5,textColor=GRIS_OSC,leading=13,alignment=TA_JUSTIFY,fontName='Helvetica-Oblique'),
    'voz_attr': _S('va',fontSize=7.5,textColor=DORADO_OSC,alignment=TA_CENTER,fontName='Helvetica-Bold',spaceBefore=4),
    'frase':    _S('fr',fontSize=8.5,textColor=GRIS_OSC,leading=13,alignment=TA_JUSTIFY,fontName='Helvetica-Oblique'),
    'frase_aut':_S('fa',fontSize=7,textColor=DORADO_OSC,alignment=TA_CENTER,fontName='Helvetica-Bold'),
    'resumen':  _S('rs',fontSize=8.5,textColor=GRIS_OSC,leading=12),
    'tbl_hdr':  _S('th',fontSize=7,textColor=BLANCO,fontName='Helvetica-Bold',alignment=TA_CENTER),
    'tbl_cell': _S('tc',fontSize=7.5,textColor=GRIS_OSC,leading=10),
    'foot_body':_S('fb',fontSize=6.5,textColor=PLAT_CL,leading=9),
    'foot_src': _S('fs',fontSize=6,textColor=GRIS_CL,leading=8),
    'puente_val':_S('pv',fontSize=16,textColor=NEGRO,fontName='Helvetica-Bold',alignment=TA_CENTER,leading=18),
    'puente_lbl':_S('pl',fontSize=6.5,textColor=GRIS_MED,alignment=TA_CENTER,leading=8),
    'tc_val':   _S('tcv',fontSize=18,textColor=DORADO,fontName='Helvetica-Bold',alignment=TA_CENTER),
}

def PS(name,**kw):
    base={k:v for k,v in vars(ST['body']).items() if k not in('name','parent') and not k.startswith('_')}
    base.pop('name',None)
    return ParagraphStyle(name,**{**base,**kw})

# ── CONSTRUCTORES BASE ─────────────────────────────────────────────────
def sec_hdr(icon,title,subtitle,accent=DORADO):
    rows=[[
        Paragraph(icon,PS('ic',fontSize=10,textColor=accent,fontName='Helvetica-Bold',alignment=TA_CENTER)),
        [Paragraph(title,ST['sec_hdr']),Paragraph(subtitle,ST['sec_label'])]
    ]]
    t=Table(rows,colWidths=[CW*0.08,CW*0.92])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG_STRIP),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LINEBEFORE',(0,0),(0,-1),4,accent),
    ]))
    return t

def stat_strip(items):
    n=len(items); cw=CW/n
    cells=[]
    for val,lbl,col in items:
        fs=16 if len(str(val))>6 else 20
        cells.append([
            Paragraph(str(val),PS('sv',fontSize=fs,textColor=col,fontName='Helvetica-Bold',alignment=TA_CENTER,leading=fs+2)),
            Paragraph(lbl,ST['stat_lbl'])
        ])
    t=Table([cells],colWidths=[cw]*n)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),PLAT_BG),('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),
        ('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
    ]))
    return t

def build_card(source,headline,body,link,style='eco'):
    accent=CMAP.get(style,AZUL); bg=BGMAP.get(style,AZUL_BG)
    alerta=[Paragraph('⚠ ALERTA MÁXIMA',PS('alr',fontSize=7,textColor=ROJO_CL,fontName='Helvetica-Bold'))] \
           if style in('red','alert') else []
    rows=[[alerta+[Paragraph(source,ST['source']),Paragraph(headline,ST['headline']),
                   Paragraph(body,ST['body']),Paragraph(f'  {link}',ST['link'])]]]
    t=Table(rows,colWidths=[CW])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),10),
        ('RIGHTPADDING',(0,0),(-1,-1),10),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
        ('LINEBEFORE',(0,0),(-1,-1),4,accent),
    ]))
    return t

def build_two_col(left,right):
    def cell(src,hl,bd,lk,st='eco'):
        return ([Paragraph(src,ST['source']),Paragraph(hl,ST['headline']),
                 Paragraph(bd,ST['body']),Paragraph(f'  {lk}',ST['link'])],
                CMAP.get(st,AZUL),BGMAP.get(st,AZUL_BG))
    lc,la,lb=cell(*left); rc,ra,rb=cell(*right)
    t=Table([[lc,rc]],colWidths=[CW*0.493,CW*0.493])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),lb),('BACKGROUND',(1,0),(1,-1),rb),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('BOX',(0,0),(0,-1),0.5,GRIS_LN),
        ('BOX',(1,0),(1,-1),0.5,GRIS_LN),('LINEBEFORE',(0,0),(0,-1),3,la),
        ('LINEBEFORE',(1,0),(1,-1),3,ra),
    ]))
    return t

def render_noticias(story,noticias):
    i=0
    while i<len(noticias):
        n=noticias[i]
        if n['tipo']=='card':
            story.append(build_card(n['fuente'],n['titular'],n['cuerpo'],n['link'],n.get('estilo','eco')))
            story.append(Spacer(1,5)); i+=1
        elif n['tipo']=='two_col':
            if i+1<len(noticias) and noticias[i+1]['tipo']=='two_col':
                n2=noticias[i+1]
                story.append(build_two_col(
                    (n['fuente'],n['titular'],n['cuerpo'],n['link'],n.get('estilo','eco')),
                    (n2['fuente'],n2['titular'],n2['cuerpo'],n2['link'],n2.get('estilo','eco'))))
                story.append(Spacer(1,5)); i+=2
            else:
                story.append(build_card(n['fuente'],n['titular'],n['cuerpo'],n['link'],n.get('estilo','eco')))
                story.append(Spacer(1,5)); i+=1
        else: i+=1

# ── SECCIONES ESPECIALES ───────────────────────────────────────────────

def render_header(story,data,logo_path=None):
    meta=data['meta']
    # Use real AESP logo — wide format
    LOGO = '/home/claude/aesp_logo_wide.png'
    if logo_path and os.path.exists(logo_path):
        LOGO = logo_path
    try:
        logo_cell = [RLImage(LOGO, width=120, height=48)]
    except:
        logo_cell = [Paragraph('AESP', PS('lg', fontSize=16, textColor=DORADO,
                                           fontName='Helvetica-Bold', alignment=TA_CENTER))]

    hdr=Table([[
        logo_cell,
        [Paragraph('BOLETÍN EJECUTIVO AESP',ST['masthead']),
         Paragraph(f"INTELIGENCIA EMPRESARIAL  |  REGIÓN FRONTERIZA NORTE  |  {meta['fecha_corta'].upper()}",ST['tagline'])],
        Paragraph('',ST['tagline'])
    ]],colWidths=[CW*0.22,CW*0.63,CW*0.15])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG_HEADER),('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(hdr); story.append(Spacer(1,3))

    ed_strip=Table([[Paragraph(f"EDICIÓN No. {meta['edicion']}  |  {meta['dia_semana']} {meta['fecha_larga']}",ST['edition'])]],colWidths=[CW])
    ed_strip.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BG_DARK),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(ed_strip); story.append(Spacer(1,5))

def render_destinatario(story,data):
    dest=data.get('destinatario',{})
    d=Table([[
        [Paragraph('ELABORADO POR:',ST['dest_label']),
         Paragraph(dest.get('elaborado_nombre','Lic. Álvaro Gutiérrez Gómez'),ST['dest_name']),
         Paragraph(dest.get('elaborado_cargo','Vicepresidente de Relaciones Públicas — AESP'),ST['dest_cargo'])],
        [Paragraph('PRESIDENTE AESP:',ST['dest_label']),
         Paragraph(dest.get('nombre','Tte. Gabriel Salazar Córdova'),ST['dest_name']),
         Paragraph(dest.get('cargo','Asociación de Empresas de Seguridad Privada — Ciudad Juárez'),ST['dest_cargo'])],
        [Paragraph('CIRCULACIÓN:',ST['dest_label']),
         Paragraph('Edición Pública',ST['dest_name']),
         Paragraph('Diaria  |  Ciudad Juárez, Chihuahua',ST['dest_cargo'])],
    ]],colWidths=[CW*0.38,CW*0.38,CW*0.24])
    d.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG_CARD),('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),10),
        ('BOX',(0,0),(-1,-1),0.5,GRIS_LN),('LINEBEFORE',(0,0),(0,-1),3,DORADO),
    ]))
    story.append(d); story.append(Spacer(1,8))

def render_resumen(story,data):
    res=data.get('resumen',{})
    items_r=res.get('items',[])
    color_map={'rr':ROJO_CL,'rr2':DORADO_OSC,'rr3':ROJO_CL,'normal':GRIS_OSC}
    res_items=[]
    for it in items_r:
        col=color_map.get(it.get('nivel','normal'),GRIS_OSC)
        bold=it.get('nivel','normal') in('rr','rr2','rr3')
        res_items.append(Paragraph(f"  {it['texto']}",
            PS('ri',fontSize=8.5,textColor=col,fontName='Helvetica-Bold' if bold else 'Helvetica',leading=12)))
        res_items.append(Spacer(1,2))

    panel=Table([[
        [Paragraph('TC / FIX BANXICO',PS('tc_l',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold')),
         Paragraph(res.get('tc','$17.40'),ST['tc_val']),
         Paragraph(res.get('tc_sub','FIX Banxico'),ST['stat_lbl'])],
        [Paragraph('CLIMA HOY',PS('cl_l',fontSize=6.5,textColor=AZUL_CL,fontName='Helvetica-Bold')),
         Paragraph(res.get('clima','28°C'),PS('cl_v',fontSize=14,textColor=AZUL,fontName='Helvetica-Bold',alignment=TA_CENTER)),
         Paragraph(res.get('clima_sub',''),ST['stat_lbl'])],
    ]],colWidths=[CW*0.5,CW*0.5])
    panel.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),DORADO_BG),('BACKGROUND',(1,0),(1,-1),AZUL_BG),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),12),('BOX',(0,0),(0,-1),0.5,GRIS_LN),
        ('BOX',(1,0),(1,-1),0.5,GRIS_LN),('LINEBEFORE',(0,0),(0,-1),3,DORADO),
        ('LINEBEFORE',(1,0),(1,-1),3,AZUL),
    ]))
    rt=Table([[
        [Paragraph('RESUMEN EJECUTIVO',ST['sec_hdr']),Spacer(1,5)]+res_items,
        panel
    ]],colWidths=[CW*0.62,CW*0.38])
    rt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),DORADO_BG),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('BOX',(0,0),(-1,-1),0.5,DORADO_CL),('LINEBEFORE',(0,0),(0,-1),4,DORADO),
    ]))
    story.append(rt); story.append(Spacer(1,8))

def render_indicadores(story,indicadores):
    if not indicadores: return
    strip=[(i['valor'],i['label'],CMAP.get(i.get('color','azul'),AZUL)) for i in indicadores]
    story.append(stat_strip(strip)); story.append(Spacer(1,5))

def render_semaforo(story,semaforo,meta):
    if not semaforo: return
    col_sem={'ALTO':ROJO_CL,'MEDIO':AMBAR,'BAJO':VERDE}
    sem_cells=[]
    for item in semaforo:
        nivel=item.get('nivel','MEDIO'); col=col_sem.get(nivel,AMBAR)
        sem_cells.append(Table([[
            CircleFl(col,14),
            [Paragraph(nivel,PS('sl',fontSize=8,textColor=col,fontName='Helvetica-Bold',alignment=TA_CENTER)),
             Paragraph(item['label'],PS('ssl',fontSize=6.5,textColor=GRIS_MED,alignment=TA_CENTER))]
        ]],colWidths=[18,CW/len(semaforo)-22]))
    sem_lbl=Table([[Paragraph(
        f"SEMÁFORO DE SEGURIDAD  —  Zona Metropolitana Juárez  —  "
        f"{meta['dia_semana']} {meta['num_dia']} {meta['fecha_larga'].split()[-2]} {meta['fecha_larga'].split()[-1]}",
        PS('sem_t',fontSize=7,textColor=BLANCO,fontName='Helvetica-Bold',alignment=TA_CENTER)
    )]],colWidths=[CW])
    sem_lbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),ACERO),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    sem_t=Table([sem_cells],colWidths=[CW/len(sem_cells)]*len(sem_cells))
    sem_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),PLAT_BG),('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
    ]))
    story.append(Spacer(1,3)); story.append(sem_lbl); story.append(sem_t); story.append(Spacer(1,8))

def render_vp(story,sec,fecha_larga,acento):
    story.append(sec_hdr(sec['id'],sec['titulo'],sec.get('subtitulo',''),acento)); story.append(Spacer(1,7))
    vp=sec.get('voz',{})
    vp_t=Table([[
        [Paragraph(vp.get('nombre','Tte. Gabriel Salazar Córdova — Presidente AESP Ciudad Juárez'),ST['voz_name']),
         Paragraph(f'"{vp.get("texto","")}"',ST['voz_body']),
         Spacer(1,4),
         Paragraph(vp.get('firma',f'— Tte. Gabriel Salazar Córdova  |  Presidente AESP  |  {fecha_larga}'),ST['voz_attr'])]
    ]],colWidths=[CW])
    vp_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG_CARD),('TOPPADDING',(0,0),(-1,-1),12),
        ('BOTTOMPADDING',(0,0),(-1,-1),12),('LEFTPADDING',(0,0),(-1,-1),18),
        ('RIGHTPADDING',(0,0),(-1,-1),18),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
        ('LINEBEFORE',(0,0),(-1,-1),4,acento),
    ]))
    story.append(vp_t); story.append(Spacer(1,7))
    frase=sec.get('frase',{})
    fr_t=Table([[
        [Paragraph(f'"{frase.get("texto","")}"',ST['frase']),
         Spacer(1,3),
         Paragraph(frase.get('firma','— Lic. Álvaro Gutiérrez Gómez  |  Vicepresidente de Relaciones Públicas  —  AESP Ciudad Juárez'),ST['frase_aut'])]
    ]],colWidths=[CW])
    fr_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),DORADO_BG),('TOPPADDING',(0,0),(-1,-1),9),
        ('BOTTOMPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),18),
        ('RIGHTPADDING',(0,0),(-1,-1),18),('BOX',(0,0),(-1,-1),0.5,DORADO_CL),
        ('LINEBEFORE',(0,0),(-1,-1),4,DORADO),
    ]))
    story.append(fr_t); story.append(Spacer(1,14))

def render_cruces(story,sec,acento):
    story.append(sec_hdr(sec['id'],sec['titulo'],sec.get('subtitulo',''),acento)); story.append(Spacer(1,7))
    # Tiempos en tiempo real
    cruces=sec.get('cruces_tiempo_real',[])
    if cruces:
        col_est={'FLUIDO':VERDE,'MODERADO':AMBAR,'LENTO':ROJO_CL,'CERRADO':ROJO}
        cells=[]
        for c in cruces:
            col=col_est.get(c.get('estado','MODERADO').upper(),AMBAR)
            cells.append([
                Paragraph(c['nombre'],PS('pn',fontSize=7.5,textColor=NEGRO,fontName='Helvetica-Bold',alignment=TA_CENTER,leading=9)),
                Paragraph(c.get('tipo','Peatonal / Auto'),ST['puente_lbl']),
                Paragraph(c.get('tiempo','~'),PS('ptv',fontSize=16,textColor=col,fontName='Helvetica-Bold',alignment=TA_CENTER,leading=18)),
                Paragraph(c.get('estado','MODERADO').upper(),PS('pest',fontSize=7,textColor=col,fontName='Helvetica-Bold',alignment=TA_CENTER)),
                Paragraph(c.get('detalle',''),ST['puente_lbl']),
            ])
        n=len(cells)
        pt=Table([cells],colWidths=[CW/n]*n)
        pt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),PLAT_BG),('TOPPADDING',(0,0),(-1,-1),6),
            ('BOTTOMPADDING',(0,0),(-1,-1),6),('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(Paragraph('TIEMPOS DE ESPERA — TIEMPO REAL  |  Fuente: reportedepuentes.com.mx / CBP',
            PS('rt',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold')))
        story.append(Spacer(1,3)); story.append(pt); story.append(Spacer(1,7))
    # FPFCH estadísticas mensuales
    fpfch=sec.get('fpfch',[])
    if fpfch:
        story.append(Paragraph('AFORO PROMEDIO DIARIO — TODOS LOS PUENTES — MARZO 2026  |  Fuente: FPFCH / Gobierno del Estado de Chihuahua',
            PS('fp',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold')))
        story.append(Spacer(1,3))
        hdr_row=[Paragraph(h,ST['tbl_hdr']) for h in ['PUENTE','TIPO','PROM. DIARIO','TENDENCIA','NOTAS']]
        rows=[hdr_row]
        for f in fpfch:
            rows.append([Paragraph(f['puente'],ST['tbl_cell']),
                        Paragraph(f['tipo'],ST['tbl_cell']),
                        Paragraph(f['promedio'],PS('td',fontSize=8,textColor=NEGRO,fontName='Helvetica-Bold',alignment=TA_CENTER)),
                        Paragraph(f.get('tendencia',''),PS('tt',fontSize=7.5,textColor=VERDE,alignment=TA_CENTER)),
                        Paragraph(f.get('notas',''),ST['tbl_cell'])])
        ft=Table(rows,colWidths=[CW*0.25,CW*0.15,CW*0.18,CW*0.15,CW*0.27])
        ft.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),BG_DARK),('ROWBACKGROUNDS',(0,1),(-1,-1),[BG_CARD,BG_CARD2]),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
            ('ALIGN',(2,0),(3,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LINEBEFORE',(0,0),(0,-1),3,PURPURA),
        ]))
        story.append(ft); story.append(Spacer(1,7))
    render_noticias(story,sec.get('noticias',[])); story.append(Spacer(1,14))

def render_alerta_empresarial(story,sec,acento):
    story.append(sec_hdr(sec['id'],sec['titulo'],sec.get('subtitulo',''),acento)); story.append(Spacer(1,7))
    alertas=sec.get('alertas',[])
    if alertas:
        hdr_row=[Paragraph(h,ST['tbl_hdr']) for h in ['TIPO DE ALERTA','DESCRIPCIÓN','ZONA / NIVEL']]
        rows=[hdr_row]
        for a in alertas:
            col_nivel={'ALTO':ROJO_CL,'MEDIO':AMBAR,'BAJO':VERDE}.get(a.get('nivel','MEDIO').upper(),AMBAR)
            rows.append([
                Paragraph(a['tipo'],ST['tbl_cell']),
                Paragraph(a['descripcion'],ST['tbl_cell']),
                Paragraph(f"{'🔴' if a.get('nivel')=='ALTO' else '🟡' if a.get('nivel')=='MEDIO' else '🟢'}  {a.get('zona','')}",
                    PS('nv',fontSize=7.5,textColor=col_nivel,fontName='Helvetica-Bold')),
            ])
        at=Table(rows,colWidths=[CW*0.28,CW*0.45,CW*0.27])
        at.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),ROJO),('ROWBACKGROUNDS',(0,1),(-1,-1),[ROJO_BG,BG_CARD2]),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
            ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,ROJO),
            ('LINEBEFORE',(0,0),(0,-1),3,ROJO),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(at); story.append(Spacer(1,7))
    render_noticias(story,sec.get('noticias',[])); story.append(Spacer(1,14))

def render_termometro(story,sec,acento):
    story.append(sec_hdr(sec['id'],sec['titulo'],sec.get('subtitulo',''),acento)); story.append(Spacer(1,7))
    if 'estadisticas' in sec:
        strip=[(e['valor'],e['label'],CMAP.get(e.get('color','azul'),AZUL)) for e in sec['estadisticas']]
        story.append(stat_strip(strip)); story.append(Spacer(1,7))
    render_noticias(story,sec.get('noticias',[]))
    # Tabla lectura estratégica
    lectura=sec.get('lectura_estrategica',[])
    if lectura:
        story.append(Spacer(1,5))
        story.append(Paragraph('LECTURA ESTRATÉGICA — RIESGOS Y OPORTUNIDADES PARA JUÁREZ',
            PS('ls',fontSize=7.5,textColor=DORADO_OSC,fontName='Helvetica-Bold')))
        story.append(Spacer(1,4))
        hdr=[Paragraph(h,ST['tbl_hdr']) for h in ['CATEGORÍA','SITUACIÓN ACTUAL','IMPLICACIÓN PARA JUÁREZ']]
        rows=[hdr]
        for l in lectura:
            col_cat={'RIESGO':ROJO_CL,'OPORTUNIDAD':VERDE,'ATENCIÓN':AMBAR}.get(l.get('tipo','ATENCIÓN').upper(),AMBAR)
            rows.append([
                Paragraph(l['categoria'],PS('lc',fontSize=7.5,textColor=col_cat,fontName='Helvetica-Bold')),
                Paragraph(l['situacion'],ST['tbl_cell']),
                Paragraph(l['implicacion'],ST['tbl_cell']),
            ])
        lt=Table(rows,colWidths=[CW*0.22,CW*0.38,CW*0.40])
        lt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),DORADO_OSC),('ROWBACKGROUNDS',(0,1),(-1,-1),[DORADO_BG,BG_CARD2]),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
            ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,DORADO_CL),
            ('LINEBEFORE',(0,0),(0,-1),3,DORADO),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(lt)
    story.append(Spacer(1,14))

def render_mx(story,sec,acento):
    story.append(sec_hdr(sec['id'],sec['titulo'],sec.get('subtitulo',''),acento)); story.append(Spacer(1,7))
    if 'estadisticas' in sec:
        strip=[(e['valor'],e['label'],CMAP.get(e.get('color','dorado'),DORADO_OSC)) for e in sec['estadisticas']]
        story.append(stat_strip(strip)); story.append(Spacer(1,7))
    render_noticias(story,sec.get('noticias',[]))
    # Tabla mercados
    mercados=sec.get('mercados',[])
    if mercados:
        story.append(Spacer(1,5))
        story.append(Paragraph(f"MERCADOS CLAVE  |  Fuente: Monex Análisis / Bloomberg",
            PS('mk',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold')))
        story.append(Spacer(1,4))
        n_cols=2; chunk=len(mercados)//2+len(mercados)%2
        left_m=mercados[:chunk]; right_m=mercados[chunk:]
        def mkt_cell(m):
            var=m.get('variacion','')
            col_v=VERDE if '+' in var else ROJO_CL if '-' in var else NEGRO
            return [Paragraph(m['activo'],PS('mv0',fontSize=7,textColor=GRIS_OSC,leading=9)),
                    Paragraph(m['valor'],PS('mv',fontSize=7.5,textColor=NEGRO,fontName='Helvetica-Bold',alignment=TA_CENTER)),
                    Paragraph(var,PS('mvr',fontSize=7,textColor=col_v,alignment=TA_CENTER)),
                    Paragraph(m.get('acum',''),PS('mac',fontSize=6.5,textColor=GRIS_MED,alignment=TA_CENTER))]
        hdr=['ACTIVO','CIERRE','VAR 1D','ACUM']
        hdr_row=[Paragraph(h,ST['tbl_hdr']) for h in hdr]
        rows_left=[hdr_row]+[mkt_cell(m) for m in left_m]
        rows_right=[hdr_row]+[mkt_cell(m) for m in right_m]
        hw=CW*0.49/4
        cws=[hw*2.2, hw*1.2, hw*0.8, hw*0.8]
        tl=Table(rows_left,colWidths=cws)
        tr=Table(rows_right,colWidths=cws) if right_m else None
        def style_mkt(t):
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),BG_DARK),('ROWBACKGROUNDS',(0,1),(-1,-1),[BG_CARD,BG_CARD2]),
                ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
                ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
                ('ALIGN',(1,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('LINEBEFORE',(0,0),(0,-1),3,DORADO_OSC),
            ]))
        style_mkt(tl)
        if tr: style_mkt(tr); story.append(Table([[tl,tr]],colWidths=[CW*0.5,CW*0.5]))
        else: story.append(tl)
    # Agenda económica
    agenda_eco=sec.get('agenda_economica',[])
    if agenda_eco:
        story.append(Spacer(1,7))
        story.append(Paragraph(f"AGENDA ECONÓMICA GLOBAL — DATOS E INDICADORES CLAVE  |  Fuente: Monex Análisis — {sec.get('fecha_agenda','')}",
            PS('ae',fontSize=6.5,textColor=DORADO_OSC,fontName='Helvetica-Bold')))
        story.append(Spacer(1,4))
        hdr2=[Paragraph(h,ST['tbl_hdr']) for h in ['FECHA','HORA','PAÍS','DATO','EST.','ANTERIOR']]
        rows2=[hdr2]
        for ag in agenda_eco:
            rows2.append([Paragraph(ag.get('fecha',''),ST['tbl_cell']),
                         Paragraph(ag.get('hora',''),ST['tbl_cell']),
                         Paragraph(ag.get('pais',''),ST['tbl_cell']),
                         Paragraph(ag.get('dato',''),ST['tbl_cell']),
                         Paragraph(ag.get('estimado','--'),PS('ae2',fontSize=7,textColor=NEGRO,fontName='Helvetica-Bold',alignment=TA_CENTER)),
                         Paragraph(ag.get('anterior','--'),PS('ae3',fontSize=7,textColor=GRIS_MED,alignment=TA_CENTER))])
        at2=Table(rows2,colWidths=[CW*0.1,CW*0.1,CW*0.1,CW*0.42,CW*0.14,CW*0.14])
        at2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),BG_DARK),('ROWBACKGROUNDS',(0,1),(-1,-1),[BG_CARD,BG_CARD2]),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
            ('INNERGRID',(0,0),(-1,-1),0.3,GRIS_LN),('BOX',(0,0),(-1,-1),0.5,GRIS_LN),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(at2)
    story.append(Spacer(1,14))

def render_fuentes(story,data):
    fuentes=data.get('fuentes_pie',[])
    if not fuentes: return
    story.append(HRFlowable(width=CW,thickness=0.5,color=GRIS_LN)); story.append(Spacer(1,5))
    story.append(Paragraph('FUENTES QUE CONSULTAMOS DIARIAMENTE',
        PS('ft_hdr',fontSize=7,textColor=DORADO_OSC,fontName='Helvetica-Bold')))
    story.append(Spacer(1,4))
    cols=3; col_w=CW/cols
    rows_f=[]; row=[]
    for i,f in enumerate(fuentes):
        row.append(Paragraph(f'• {f}',ST['foot_src']))
        if (i+1)%cols==0:
            rows_f.append(row); row=[]
    if row:
        while len(row)<cols: row.append(Paragraph('',ST['foot_src']))
        rows_f.append(row)
    if rows_f:
        ft=Table(rows_f,colWidths=[col_w]*cols)
        ft.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),('LEFTPADDING',(0,0),(-1,-1),4),('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.append(ft)
    story.append(Spacer(1,8))

def render_footer(story,data):
    meta=data['meta']
    story.append(HRFlowable(width=CW,thickness=1,color=DORADO)); story.append(Spacer(1,4))
    # Signature row
    sig=Table([[
        [Paragraph('Boletín elaborado por:',PS('sig0',fontSize=6,textColor=DORADO_OSC,fontName='Helvetica-Bold')),
         Paragraph('Lic. Álvaro Gutiérrez Gómez',PS('sig1',fontSize=8,textColor=NEGRO,fontName='Helvetica-Bold')),
         Paragraph('Vicepresidente de Relaciones Públicas  |  AESP Ciudad Juárez',PS('sig2',fontSize=6.5,textColor=GRIS_MED))],
        [Paragraph('ASOCIACIÓN DE EMPRESAS DE SEGURIDAD PRIVADA',PS('sig3',fontSize=6,textColor=DORADO_OSC,fontName='Helvetica-Bold')),
         Paragraph('DE CIUDAD JUÁREZ (AESP)',PS('sig4',fontSize=7.5,textColor=NEGRO,fontName='Helvetica-Bold')),
         Paragraph(f"Edición No. {meta['edicion']}  |  {meta['fecha_larga']}",PS('sig5',fontSize=6.5,textColor=GRIS_MED))],
    ]],colWidths=[CW*0.5,CW*0.5])
    sig.setStyle(TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBEFORE',(0,0),(0,-1),2,DORADO),
    ]))
    story.append(sig); story.append(Spacer(1,5))
    # Footer bar
    ft=Table([[Paragraph(
        f"Boletín de circulación pública — AESP Ciudad Juárez  |  "
        f"Información verificada con fuentes públicas  |  "
        f"Próxima edición: {meta['proxima_edicion']}",
        ST['foot_body'])]],colWidths=[CW])
    ft.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BG_DARK),('TOPPADDING',(0,0),(-1,-1),7),
                            ('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(ft)

# ── CONSTRUCTOR PRINCIPAL ──────────────────────────────────────────────
def build_boletin(data,output_path,logo_path=None):
    story=[]
    meta=data['meta']
    render_header(story,data,logo_path)
    render_destinatario(story,data)
    render_resumen(story,data)
    render_indicadores(story,data.get('indicadores',[]))
    render_semaforo(story,data.get('semaforo',[]),meta)

    SPECIAL={'[VP]','[P]','[AE]','[TE]','[MX]'}
    for sec in data.get('secciones',[]):
        sid=sec['id']; acento=ACCENT_MAP.get(sec.get('acento','dorado'),DORADO)
        if sid=='[VP]':   render_vp(story,sec,meta['fecha_larga'],acento)
        elif sid=='[P]':  render_cruces(story,sec,acento)
        elif sid=='[AE]': render_alerta_empresarial(story,sec,acento)
        elif sid=='[TE]': render_termometro(story,sec,acento)
        elif sid=='[MX]': render_mx(story,sec,acento)
        else:
            story.append(sec_hdr(sid,sec['titulo'],sec.get('subtitulo',''),acento))
            story.append(Spacer(1,7))
            if 'estadisticas' in sec:
                strip=[(e['valor'],e['label'],CMAP.get(e.get('color','azul'),AZUL)) for e in sec['estadisticas']]
                story.append(stat_strip(strip)); story.append(Spacer(1,7))
            render_noticias(story,sec.get('noticias',[]))
            story.append(Spacer(1,14))

    render_fuentes(story,data)
    render_footer(story,data)

    doc=SimpleDocTemplate(output_path,pagesize=letter,
        leftMargin=inch,rightMargin=inch,topMargin=0.5*inch,bottomMargin=0.5*inch,
        title=f"Boletín Ejecutivo AESP — Edición No.{meta['edicion']} — {meta['fecha_larga']}")
    doc.build(story)
    print(f"OK: {output_path}")

if __name__=='__main__':
    if len(sys.argv)<2:
        print("Uso: python3 aesp_motor_v2.py noticias_HOY.json [output.pdf]")
        sys.exit(1)
    jpath=sys.argv[1]
    with open(jpath,'r',encoding='utf-8') as f: data=json.load(f)
    logo=sys.argv[3] if len(sys.argv)>3 else None
    out=sys.argv[2] if len(sys.argv)>2 else f"/mnt/user-data/outputs/Boletin_AESP_Ed{data['meta']['edicion']}.pdf"
    build_boletin(data,out,logo)
