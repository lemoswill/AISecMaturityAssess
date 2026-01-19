
import base64
import datetime
import pandas as pd
from io import BytesIO

def generate_html_report(metrics, charts, details_df, metadata):
    """
    Generates a professional HTML report optimized for Print-to-PDF.
    
    Args:
        metrics (dict): Key metrics (score, maturity, gaps, compliance)
        charts (dict): Plotly figures {'gauge': fig, 'radar': fig, 'benchmark': fig}
        details_df (pd.DataFrame): Detailed assessment data
        metadata (dict): Assessment metadata (org, project, date)
    """
    
    # 1. Convert Charts to HTML (Embeddable)
    # responsive=True ensures they fit the printable area
    gauge_html = charts['gauge'].to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
    radar_html = charts['radar'].to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False})
    bench_html = charts['benchmark'].to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False})
    
    risk_html = ""
    if charts.get('risk'):
        risk_html = charts['risk'].to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False})
    
    # 2. Prepare Data Table HTML
    # Select cols
    cols = ['category', 'question_id', 'Requirement', 'score', 'notes', 'NIST GenAI (600-1)', 'ISO 27001']
    # Renaming
    rename = {
        'category': 'Function',
        'question_id': 'ID',
        'score': 'Score',
        'notes': 'Notes/Justification',
        'Requirement': 'Control'
    }
    
    # Filter available cols
    available_cols = [c for c in cols if c in details_df.columns]
    table_df = details_df[available_cols].rename(columns=rename)
    
    # Clean up empty notes
    if 'Notes/Justification' in table_df.columns:
        table_df['Notes/Justification'] = table_df['Notes/Justification'].fillna("-")
        
    table_html = table_df.to_html(index=False, classes="table table-striped", border=0)

    # 3. HTML Template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Security Maturity Report</title>
        <meta charset="utf-8">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                color: #0F172A;
                line-height: 1.5;
                margin: 0;
                padding: 40px;
                background: white;
            }}
            .header {{
                border-bottom: 2px solid #3B82F6;
                padding-bottom: 20px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .logo {{
                font-size: 24px;
                font-weight: 800;
                color: #1E293B;
            }}
            .meta {{
                text-align: right;
                font-size: 14px;
                color: #64748B;
            }}
            h1 {{ font-size: 28px; font-weight: 800; color: #1E293B; margin-bottom: 5px; }}
            h2 {{ font-size: 18px; font-weight: 600; color: #334155; margin-top: 30px; margin-bottom: 15px; border-left: 4px solid #3B82F6; padding-left: 10px; }}
            
            /* KPI Cards */
            .kpi-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 40px;
            }}
            .kpi-card {{
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 15px;
                background: #F8FAFC;
                text-align: center;
            }}
            .kpi-val {{ font-size: 24px; font-weight: 800; color: #0F172A; display: block; }}
            .kpi-label {{ font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; }}
            
            /* Charts Layout */
            .charts-row {{
                display: flex;
                margin-bottom: 20px;
                page-break-inside: avoid;
            }}
            .chart-box {{
                flex: 1;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px;
                margin: 0 10px;
                background: white;
            }}
            
            /* Table */
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                margin-top: 10px;
            }}
            th {{ background: #F1F5F9; color: #475569; font-weight: 600; text-align: left; padding: 8px; border-bottom: 2px solid #E2E8F0; }}
            td {{ padding: 8px; border-bottom: 1px solid #E2E8F0; vertical-align: top; }}
            tr:nth-child(even) {{ background: #F8FAFC; }}
            
            /* Logic for Score Colors */
            td:nth-child(4) {{ font-weight: bold; }} 
            
            /* Footer */
            .footer {{
                margin-top: 50px;
                border-top: 1px solid #E2E8F0;
                padding-top: 20px;
                text-align: center;
                font-size: 10px;
                color: #94A3B8;
            }}
            
            @media print {{
                body {{ padding: 0; }}
                .no-print {{ display: none; }}
                .page-break {{ page-break-after: always; }}
                .chart-box {{ break-inside: avoid; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <div class="logo">🛡️ AI Security Maturity Assessment</div>
                <div style="font-size: 14px; color: #64748B;">Executive Summary & Compliance Report</div>
            </div>
            <div class="meta">
                <strong>Org:</strong> {metadata.get('org', 'Unknown')}<br>
                <strong>Date:</strong> {metadata.get('date', datetime.date.today())}<br>
                <strong>Scope:</strong> {metadata.get('scope', 'Organization')}
            </div>
        </div>
        
        <!-- KPI Section -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <span class="kpi-val" style="color: {'#10B981' if metrics['score'] > 4 else '#F59E0B' if metrics['score'] > 2.5 else '#EF4444'}">{metrics['score']:.1f} / 5.0</span>
                <span class="kpi-label">Overall Maturity</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-val">{metrics['maturity']}</span>
                <span class="kpi-label">Current Level</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-val" style="color: #EF4444">{metrics['gaps']}</span>
                <span class="kpi-label">Critical Gaps</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-val" style="color: #3B82F6">${metrics.get('savings', 0)/1000000:.1f}M</span>
                <span class="kpi-label">Financial Risk Reduction</span>
            </div>
        </div>
        
        <h2>📊 Strategic Analysis</h2>
        <div class="charts-row">
            <div class="chart-box" style="flex: 0 0 300px;">
                {gauge_html}
            </div>
            <div class="chart-box">
                {radar_html}
            </div>
        </div>
        
        <div class="charts-row">
             <div class="chart-box">
                <h3 style="text-align: center; font-size: 14px; margin-top: 0;">Benchmark vs Industry</h3>
                {bench_html}
            </div>
             <div class="chart-box">
                <h3 style="text-align: center; font-size: 14px; margin-top: 0;">Risk Analysis: Impact vs Prob.</h3>
                {risk_html}
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <h2>📋 Detailed Assessment & Compliance Matrix</h2>
        {table_html}
        
        <div class="footer">
            Generated by AI Security Maturity Assessment Tool • Confidential • {datetime.date.today().year}
        </div>
        
        <script>
            // Auto open print dialog
            // window.print(); 
        </script>
    </body>
    </html>
    """
    
    return html
