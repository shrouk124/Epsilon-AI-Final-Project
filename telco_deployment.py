import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# ─── إعدادات الصفحة ───
st.set_page_config(
    layout='wide',
    page_title='توقع هجران عملاء الاتصالات',
    page_icon='📡'
)



ACCENT   = '#5b8dee'  
RISK_CLR = "#b07a3d"   
SAFE_CLR = "#395489"   

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* {{ font-family: 'Cairo', sans-serif !important; }}
html, body, [class*="css"] {{ direction: rtl; }}

.stApp {{ background-color: #0e1117; color: #f0f2f6; }}

section[data-testid="stSidebar"] {{
    background-color: #1a1d23;
    border-left: 2px solid {ACCENT};
}}

.stSelectbox label, .stSlider label,
.stNumberInput label, .stRadio label {{
    color: #a0a8b8 !important;
    font-size: 14px;
}}

div[data-testid="stSelectbox"] > div:first-child {{ background-color: #1e222a; }}

button[data-baseweb="tab"] {{
    font-size: 16px !important;
    font-weight: 600 !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, {ACCENT}, #3a6fd8);
    color: white;
    font-family: 'Cairo', sans-serif !important;
    font-size: 18px;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: all 0.3s;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #3a6fd8, #2a5fc8);
    transform: scale(1.02);
}}

.header-banner {{
    background: linear-gradient(135deg, #1a1d23, #0e1117);
    border: 1px solid {ACCENT};
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    margin-bottom: 20px;
}}

.section-label {{
    color: {ACCENT};
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid #2a2e36;
}}

div[data-testid="stVerticalBlock"] > div {{ gap: 0.4rem; }}
</style>
""", unsafe_allow_html=True)

# ─── العنوان الرئيسي ───
st.markdown(f"""
<div class="header-banner">
    <h1 style="color:{ACCENT}; font-size:2rem; margin:0;">📡 نظام التنبؤ بهجران عملاء الاتصالات</h1>
    <p style="color:#a0a8b8; font-size:0.95rem; margin-top:6px;">
        أدخل بيانات العميل واضغط على زر التنبؤ لمعرفة احتمالية الهجران
    </p>
</div>
""", unsafe_allow_html=True)

#  تحميل النموذج  
model  = joblib.load('churn_model.pkl')
df_ref = pd.read_csv('cleaned_telco.csv', index_col=0)


contract_map = {
    'شهري'     : 'Month-to-month',
    'سنة واحدة': 'One year',
    'سنتان'    : 'Two year',
}

# ─── الشريط الجانبي ───
with st.sidebar:
    st.markdown(f"## ⚙️ البيانات الرقمية")
    tenure = st.slider(
        'مدة الاشتراك (بالأشهر)',
        int(df_ref['tenure'].min()),
        int(df_ref['tenure'].max()),
        value=12, step=1
    )
    monthly_chg = st.number_input(
        'الرسوم الشهرية ($)',
        min_value=float(df_ref['MonthlyCharges'].min()),
        max_value=float(df_ref['MonthlyCharges'].max()),
        value=65.0, step=0.5
    )

    total_chg = float(tenure * monthly_chg)

    st.markdown("---")
    st.metric(label="إجمالي الرسوم ($)", value=f"${total_chg:,.2f}")

# المدخلات 
tab1, tab2 = st.tabs(["👤 البيانات الشخصية والعقد", "📶 الخدمات المشتركة"])

with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="section-label">البيانات الشخصية</div>', unsafe_allow_html=True)
        gender_ar = st.selectbox('الجنس', ['ذكر', 'أنثى'])
        gender    = 'Male' if gender_ar == 'ذكر' else 'Female'

        senior_ar = st.selectbox('كبير السن؟', ['لا', 'نعم'])
        senior    = 1 if senior_ar == 'نعم' else 0

    with col2:
        st.markdown('<div class="section-label">الوضع الاجتماعي</div>', unsafe_allow_html=True)
        partner_ar   = st.selectbox('لديه شريك/ة؟',       ['لا', 'نعم'])
        partner      = 'Yes' if partner_ar == 'نعم' else 'No'

        dependent_ar = st.selectbox('لديه أفراد يعولهم؟', ['لا', 'نعم'])
        dependents   = 'Yes' if dependent_ar == 'نعم' else 'No'

    with col3:
        st.markdown('<div class="section-label">بيانات العقد</div>', unsafe_allow_html=True)
        contract_ar = st.selectbox('نوع العقد', list(contract_map.keys()))
        contract    = contract_map[contract_ar]

        paperless_ar = st.selectbox('فاتورة إلكترونية؟', ['لا', 'نعم'])
        paperless    = 'Yes' if paperless_ar == 'نعم' else 'No'

    
        payment_map = {
    "Electronic check": "شيك إلكتروني",
    "Mailed check": "شيك بريدي",
    "Bank transfer (automatic)": "تحويل بنكي (تلقائي)",
    "Credit card (automatic)": "بطاقة ائتمان (تلقائي)"
    }

    payment_ar = st.selectbox(
        
        "طريقة الدفع",
        list(payment_map.values())
    )

# تحويل الاختيار للعربي إلى الإنجليزي
payment = {v: k for k, v in payment_map.items()}[payment_ar]

with tab2:
    col4, col5 = st.columns(2)

    with col4:
        st.markdown('<div class="section-label">خدمة الهاتف</div>', unsafe_allow_html=True)
        phone_ar  = st.selectbox('خدمة الهاتف', ['لا', 'نعم'])
        phone_svc = 'Yes' if phone_ar == 'نعم' else 'No'

        if phone_svc == 'Yes':
            multi_ar    = st.selectbox('خطوط متعددة', ['لا', 'نعم'])
            multi_lines = 'Yes' if multi_ar == 'نعم' else 'No'
        else:
            multi_lines = 'No phone service'
            st.caption("ℹ️ تم تعيين الخطوط المتعددة تلقائياً.")

    with col5:
        st.markdown('<div class="section-label">خدمة الإنترنت</div>', unsafe_allow_html=True)
    
        internet = st.selectbox('نوع الإنترنت', ['Fiber optic', 'DSL', 'No'])

    if internet != 'No':
        st.markdown('<div class="section-label" style="margin-top:12px;">⬇️ خدمات الإنترنت الإضافية</div>', unsafe_allow_html=True)
        ic1, ic2, ic3 = st.columns(3)

        with ic1:
            sec_ar      = st.selectbox('الأمن الإلكتروني', ['لا', 'نعم'])
            online_sec  = 'Yes' if sec_ar  == 'نعم' else 'No'
            bkp_ar      = st.selectbox('النسخ الاحتياطي', ['لا', 'نعم'])
            online_bkp  = 'Yes' if bkp_ar  == 'نعم' else 'No'
        with ic2:
            prot_ar     = st.selectbox('حماية الأجهزة',   ['لا', 'نعم'])
            dev_protect = 'Yes' if prot_ar  == 'نعم' else 'No'
            sup_ar      = st.selectbox('الدعم التقني',     ['لا', 'نعم'])
            tech_support= 'Yes' if sup_ar   == 'نعم' else 'No'
        with ic3:
            tv_ar       = st.selectbox('بث التلفاز',       ['لا', 'نعم'])
            stream_tv   = 'Yes' if tv_ar    == 'نعم' else 'No'
            mov_ar      = st.selectbox('بث الأفلام',       ['لا', 'نعم'])
            stream_mov  = 'Yes' if mov_ar   == 'نعم' else 'No'
    else:
        online_sec = online_bkp = dev_protect = tech_support = stream_tv = stream_mov = 'No internet service'
        st.info("ℹ️ تم تعيين خدمات الإنترنت الإضافية تلقائياً (لا توجد خدمة إنترنت).")

# ─── Feature Engineering 
def get_tenure_group(t):
    if t <= 12:   return 'New Customer'
    elif t <= 36: return 'Mid-term Customer'
    else:         return 'Long-term Customer'

charges_per_tenure = total_chg / (tenure + 1)
num_services = sum([
    1 if online_sec   == 'Yes' else 0,
    1 if online_bkp   == 'Yes' else 0,
    1 if dev_protect  == 'Yes' else 0,
    1 if tech_support == 'Yes' else 0,
    1 if stream_tv    == 'Yes' else 0,
    1 if stream_mov   == 'Yes' else 0,
])
tenure_grp = get_tenure_group(tenure)

col_order = [c for c in df_ref.columns if c != 'Churn']

new_data = pd.DataFrame([[
    gender, senior, partner, dependents, tenure,
    phone_svc, multi_lines, internet, online_sec, online_bkp,
    dev_protect, tech_support, stream_tv, stream_mov,
    contract, paperless, payment, monthly_chg, total_chg,
    tenure_grp, charges_per_tenure, num_services
]], columns=col_order)

# ضيفي السطور دي للتصحيح
st.write("---")
st.write("بيانات المدخلات:", new_data)
st.write("أعمدة الموديل:", model.feature_names_in_) # دي هتوريكي الأعمدة اللي الموديل مستنيها بالظبط


#  زر التنبؤ 
st.markdown("<br>", unsafe_allow_html=True)
if st.button('🔮 تنبأ باحتمالية الهجران'):

    prediction  = model.predict(new_data)[0]
    probability = model.predict_proba(new_data)[0][1]

    st.markdown("---")
    st.markdown("## 📊 نتيجة التنبؤ")

    res_col1, res_col2 = st.columns([1, 1])

    with res_col1:
        gauge_color = RISK_CLR if probability > 0.5 else SAFE_CLR
        fig = go.Figure(go.Indicator(
            mode  = "gauge+number+delta",
            value = round(probability * 100, 1),
            number= {'suffix': '%', 'font': {'size': 36, 'family': 'Cairo', 'color': gauge_color}},
            title = {'text': 'احتمالية الهجران', 'font': {'size': 20, 'family': 'Cairo', 'color': '#f0f2f6'}},
            delta = {
                'reference'  : 50,
                'increasing' : {'color': RISK_CLR},
                'decreasing' : {'color': SAFE_CLR}
            },
            gauge = {
                'axis'       : {'range': [0, 100], 'tickfont': {'family': 'Cairo'}},
                'bar'        : {'color': gauge_color, 'thickness': 0.25},
                'bgcolor'    : '#1e222a',
                'borderwidth': 2,
                'bordercolor': '#2a2e36',
                'steps'      : [
                    {'range': [0,  40], 'color': '#1c2233'},   
                    {'range': [40, 70], 'color': '#2a2218'},  
                    {'range': [70,100], 'color': '#2a1c12'}, 
                ],
                'threshold'  : {
                    'line'     : {'color': '#8899bb', 'width': 3},
                    'thickness': 0.8,
                    'value'    : 50
                }
            }
        ))
        fig.update_layout(
            paper_bgcolor='#0e1117',
            plot_bgcolor ='#0e1117',
            height=320,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with res_col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if prediction == 1:
            st.warning("""
## ⚠️ تنبيه: خطر هجران مرتفع

هذا العميل معرض لخطر مغادرة الخدمة في الفترة القادمة.

**الإجراءات المقترحة للاحتفاظ به:**
- 🎁 قدّم له عرضاً مميزاً لتجديد أو تمديد العقد الحالي.
- 📞 تواصل معه فوراً من خلال فريق الدعم أو مبيعات الاحتفاظ بالعملاء.
- 💡 اقترح ترقية باقة الإنترنت الخاصة به بأسعار تفضيلية.
""")
        else:
            st.info("""
## ✅ العميل مستقر ومنتمي

هذا العميل راضٍ عن الخدمة المقدمة ومن المرجح استمراره مع الشركة.

**الإجراءات المقترحة:**
- 🌟 حافظ على جودة الخدمة الحالية وقنوات التواصل المستمرة معه.
- 🔄 اقترح عليه بعض الخدمات المضافة (Add-ons) المناسبة لاهتماماته.
""")
