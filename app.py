import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

st.set_page_config(page_title="초파리 디지털 트윈", layout="wide")
st.title("🪰 초파리 디지털 트윈")

# Streamlit Secrets(보안 설정)에서 API 키를 안전하게 불러옴
MY_GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")


st.markdown("### 🧪 유전자 / 약물 / 환경 변인 설정")
col_a, col_b, col_c, col_d, col_e = st.columns([2.2, 2.2, 2, 2, 2])

with col_a:
    gene = st.selectbox("🧬 유전자 돌연변이", [
        "Wild Type (야생형)", 
        "White Gene Mut (흰 눈 변이)", 
        "Vestigial Mut (날개 퇴화 변이)", 
        "Shibire TS Mut (온도 신경마비)"
    ])
with col_b:
    drug = st.selectbox("💉 인간 호환 3대 투여 약물", [
        "None (대조군)", 
        "Caffeine (중추신경 자극 / 심박 가속)", 
        "Paraquat (신경독소 / 파킨슨 모델)", 
        "Resveratrol (항산화 / 항노화제)"
    ])
with col_c:
    temp = st.slider("🌡️ 환경: 온도 (℃)", 15, 35, 25)
with col_d:
    light = st.slider("☀️ 환경: 광량 (Lux)", 0, 1000, 300)
with col_e:
    humidity = st.slider("💧 환경: 습도 (%)", 20, 90, 60)

# 生物學 대사 연산
temp_penalty = abs(temp - 25) * 3
hum_penalty = abs(humidity - 60) * 0.5
surv_wild = max(5, 100 - temp_penalty - hum_penalty)

surv_mut = surv_wild
cause_note = ""
advantage_note = ""
drug_effect = ""
gene_penalty = 0

if "Wild Type" in gene:
    cause_note = "정상 야생형 게놈."
    advantage_note = "기본 자연 환경 최적 생존."
elif "White Gene" in gene:
    cause_note = "ABC 수송체 유전자 결손 (인간 ABCB1 상동 유전자)."
    if light > 500:
        gene_penalty = (light - 500) // 10
        surv_mut -= gene_penalty
        advantage_note = f"❌ 강한 빛(Lux {light}): 시각 신경 광독성 발생!"
    else:
        surv_mut += 5
        advantage_note = "✅ 어두운 조건: 색소 대사 에너지 절약."
elif "Vestigial" in gene:
    cause_note = "날개 전사 인자 결손."
    if temp > 28:
        gene_penalty = (temp - 28) * 7
        surv_mut -= gene_penalty
        advantage_note = f"❌ 고온({temp}℃): 체온 조절 및 비행 불가."
    else:
        advantage_note = "⚠️ 강풍 도서 환경: 바람에 휩쓸리지 않음."
elif "Shibire" in gene:
    cause_note = "Dynamin 변이 (인간 DNM1 상동 유전자)."
    if temp >= 29:
        surv_mut = 0
        advantage_note = f"🚨 {temp}℃ 고온: 신경 전달 차단으로 전신 마비 사멸!"
    else:
        advantage_note = "✅ 28℃ 이하: 정상 신경 전달 유지."

drug_penalty = 0
if "Caffeine" in drug:
    drug_penalty = -8
    surv_mut += drug_penalty
    drug_effect = "⚡ 카페인: 뇌 신경 과활성화(노란빛) 및 심박수 급증(붉은 맥동), 대사 가속."
elif "Paraquat" in drug:
    drug_penalty = -35
    surv_mut += drug_penalty
    drug_effect = "☠️ 파라콰트: 뇌 파킨슨 유사 손상(회색) 및 소화관 중독 괴사(보라색)."
elif "Resveratrol" in drug:
    drug_penalty = 10
    surv_mut += drug_penalty
    drug_effect = "🛡️ 레스베라트롤: 뇌/소화관 항산화 회복(청록색 발광) 및 스트레스 완화."
else:
    drug_effect = "🟢 미투여 대조군: 기본 생리 대사 유지."

surv_mut = max(0, min(100, surv_mut))

st.markdown("---")
col1, col2 = st.columns([1.1, 0.9])

with col1:
    st.subheader("🧊 실시간 생체 장기 투시 모델 (Drosophila Model)")
    
    is_white_val = 1 if "White Gene" in gene else 0
    is_vestigial_val = 1 if "Vestigial" in gene else 0
    is_shibire_val = 1 if ("Shibire" in gene and temp >= 29) else 0

    drug_type_val = "none"
    if "Caffeine" in drug: drug_type_val = "caffeine"
    elif "Paraquat" in drug: drug_type_val = "paraquat"
    elif "Resveratrol" in drug: drug_type_val = "resveratrol"

    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body { margin:0; background:#0d0e15; overflow:hidden; font-family:sans-serif; }
        #cv { width:100%; height:380px; display:block; background:#0d0e15; }
        .legend { position:absolute; top:10px; left:10px; background:rgba(0,0,0,0.85); color:white; padding:10px; border-radius:6px; font-size:12px; pointer-events:none; border:1px solid #333; line-height:1.6; z-index:10; }
      </style>
    </head>
    <body>
    <div class="legend">
      🔵 뇌 (Brain): 약물 반응 시각화<br>
      🔴 심장 (Heart): 등맥 심박 맥동 렌더링<br>
      🟢 소화관 (Gut): 약물 대사관<br>
      🧪 약물: <span style="color:#89b4fa;font-weight:bold;">""" + str(drug) + """</span>
    </div>
    <canvas id="cv"></canvas>
    <script>
      const cv = document.getElementById('cv');
      const ctx = cv.getContext('2d');
      
      const isWhite = """ + str(is_white_val) + """;
      const isVestigial = """ + str(is_vestigial_val) + """;
      const isShibire = """ + str(is_shibire_val) + """;
      const dType = '""" + str(drug_type_val) + """';

      function resize() {
        cv.width = cv.clientWidth || 500;
        cv.height = 380;
      }
      resize();

      let pulse = 0;

      function draw() {
        ctx.clearRect(0, 0, cv.width, cv.height);
        const cx = cv.width / 2;
        const cy = cv.height / 2 + 10;

        // 1. 투명 껍질 (Head, Thorax, Abdomen)
        ctx.fillStyle = "rgba(200, 159, 101, 0.25)";
        ctx.strokeStyle = "rgba(200, 159, 101, 0.6)";
        ctx.lineWidth = 2;

        ctx.beginPath(); ctx.arc(cx - 120, cy, 35, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(cx - 40, cy, 50, 40, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(cx + 60, cy, 70, 35, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

        // 2. 복눈 (상/하 좌우 짝)
        ctx.fillStyle = (isWhite === 1) ? "#ffffff" : "#d90429";
        ctx.beginPath(); ctx.arc(cx - 135, cy - 15, 14, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(cx - 135, cy + 15, 14, 0, Math.PI * 2); ctx.fill();

        // 3. 양쪽 날개 2짝 (위쪽 날개 & 아래쪽 날개 쌍)
        ctx.fillStyle = "rgba(224, 230, 237, 0.4)";
        ctx.strokeStyle = "rgba(255, 255, 255, 0.7)";
        if (isVestigial === 1) {
          // 퇴화된 소형 날개 2짝
          ctx.beginPath(); ctx.ellipse(cx - 30, cy - 35, 25, 10, -0.4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
          ctx.beginPath(); ctx.ellipse(cx - 30, cy + 35, 25, 10, 0.4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        } else {
          // 정상 날개 2짝 (위/아래 대칭)
          ctx.beginPath(); ctx.ellipse(cx - 10, cy - 55, 85, 22, -0.3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
          ctx.beginPath(); ctx.ellipse(cx - 10, cy + 55, 85, 22, 0.3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }

        // 4. 내부 장기 약물 색상
        let bColor = "#0066ff", hColor = "#ff0055", gColor = "#00cc44";
        let pSpeed = 0.05;

        if (dType === "caffeine") {
          bColor = "#ffff00"; hColor = "#ff0000"; pSpeed = 0.18;
        } else if (dType === "paraquat") {
          bColor = "#555555"; gColor = "#aa00aa"; pSpeed = 0.02;
        } else if (dType === "resveratrol") {
          bColor = "#00ffff"; gColor = "#00ffaa"; pSpeed = 0.06;
        }

        if (isShibire === 1) { bColor = "#ff0000"; }

        // 뇌
        ctx.fillStyle = bColor; ctx.shadowColor = bColor; ctx.shadowBlur = 15;
        ctx.beginPath(); ctx.arc(cx - 110, cy, 18, 0, Math.PI * 2); ctx.fill();

        // 소화관
        ctx.fillStyle = gColor; ctx.shadowColor = gColor; ctx.shadowBlur = 10;
        ctx.beginPath(); ctx.ellipse(cx + 50, cy + 5, 45, 12, 0, 0, Math.PI * 2); ctx.fill();

        // 심장 맥동
        pulse += pSpeed;
        const hScale = 1 + Math.sin(pulse) * 0.25;
        ctx.fillStyle = hColor; ctx.shadowColor = hColor; ctx.shadowBlur = 20;
        ctx.beginPath(); ctx.ellipse(cx - 35, cy - 10, 30 * hScale, 8 * hScale, 0, 0, Math.PI * 2); ctx.fill();
        
        ctx.shadowBlur = 0;
        requestAnimationFrame(draw);
      }

      draw();
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=390)

    st.info("💡 **초파리 모델 활용 의의:** 초파리는 인간 질병 관련 유전자와 **약 75%의 상동성**을 공유하여, 실제 임상 전 신약 약물 독성 및 생체 장기 대사 반응을 가상 예측하는 최적의 바이오 디지털 트윈 모델입니다.")

with col2:
    st.subheader("📊 적응도 & 약물 대사 평가")
    st.info(f"**🔬 유전자 메커니즘:** {cause_note}")
    st.success(f"**💉 약물 투여 대사 반응:**\n{drug_effect}")
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("🌿 야생형 생존율", f"{int(surv_wild)}%")
    with m2:
        st.metric("🧬 변이주+약물 생존율", f"{int(surv_mut)}%", delta=f"{int(surv_mut - surv_wild)}%p")

    with st.expander("❓ 생존율 수치 연산 공식 보기"):
        st.markdown(f"""
        **[적응도 & 생존율 수치 계산 알고리즘]**
        
        1. **야생형 기본 생존율 기준:** `100%` (최적 조건: 25℃, 습도 60%)
        2. **환경 감점 요인:**
           - 온도 페널티: `|현재온도({temp}℃) - 25| × 3%` (감점: **-{temp_penalty}%**)
           - 습도 페널티: `|현재습도({humidity}%) - 60| × 0.5%` (감점: **-{hum_penalty}%**)
           - 야생형 생존율 = `100 - {temp_penalty} - {hum_penalty}` = **{int(surv_wild)}%**
        3. **유전자 및 약물 복합 가감점:**
           - 유전자 변이 영향: **-{gene_penalty}%p**
           - 약물 투여 영향: **{drug_penalty}%p**
           - 최종 변이주 생존율 = **{int(surv_mut)}%**
        """)

    st.warning(f"**⚖️ 환경 적응 평가:**\n{advantage_note}")
    st.markdown("---")
    
    st.subheader("💬 Groq AI 유전체 대사 대화창")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("🚀 유전체·약물 복합 대사 심층 AI 분석", use_container_width=True):
        client = Groq(api_key=MY_GROQ_KEY)
        prompt = f"""
        초파리 디지털 트윈 약물/환경 분석 보고서:
        - 유전자: {gene} | 투여 약물: {drug}
        - 환경: 온도 {temp}℃, 조도 {light} Lux, 습도 {humidity}%
        - 야생형 생존율: {surv_wild}%, 변이주+약물 생존율: {surv_mut}%

        [작성 요청]
        1. 약물({drug})이 해당 변이주의 주요 장기(뇌, 심장, 소화관)에 미치는 생물학적 영향
        2. 인간 질환 모델 관점에서의 약물 반응 동질성 및 시사점
        """
        with st.spinner("AI 분석 중..."):
            try:
                res = client.chat.completions.create(model="openai/gpt-oss-120b", messages=[{"role":"user", "content":prompt}])
                ai_ans = res.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": ai_ans})
            except Exception as e:
                try:
                    res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"user", "content":prompt}])
                    ai_ans = res.choices[0].message.content
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "assistant", "content": ai_ans})
                except Exception as e2:
                    st.error(f"Groq API 오류: {e2}")

    chat_container = st.container(height=320)
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])
            elif msg["role"] == "user" and not msg["content"].startswith("초파리 디지털 트윈"):
                with st.chat_message("user"):
                    st.markdown(msg["content"])

    if user_query := st.chat_input("약물 반응이나 유전자 메커니즘에 대해 질문하세요..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        client = Groq(api_key=MY_GROQ_KEY)
        try:
            res = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
        except Exception as e:
            st.error(f"Groq 오류: {e}")
