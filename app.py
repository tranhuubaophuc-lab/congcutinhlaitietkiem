import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Công Cụ Tính Lãi Tiết Kiệm", page_icon="💰", layout="wide")

st.title("💰 Ứng Dụng Tính Lãi Suất Tiết Kiệm")
st.markdown("Tính toán chi tiết số tiền lãi nhận được theo lãi đơn hoặc lãi kép với nhiều hình thức trả lãi.")

# Layout chia làm 2 cột
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("📥 Nhập thông tin")
    
    # Nhập liệu
    principal = st.number_input("Số tiền gửi (VNĐ):", min_value=0, value=100000000, step=1000000)
    term = st.number_input("Kỳ hạn gửi (tháng):", min_value=1, value=12, step=1)
    
    interest_rate = st.number_input("Lãi suất (%/năm):", min_value=0.0, value=6.0, step=0.1)
    
    interest_type = st.radio("Loại lãi suất:", options=["Lãi đơn", "Lãi kép (Nhập gốc)"], horizontal=True)
    
    frequency = st.selectbox("Hình thức lãnh/nhập lãi:", 
                             options=["Lãnh lãi theo tháng", "Lãnh lãi theo quý", "Lãnh lãi cuối kỳ"])

with col2:
    st.header("📊 Kết quả tính toán")
    
    # Xác định số tháng trong 1 kỳ
    if frequency == "Lãnh lãi theo tháng":
        period_months = 1
    elif frequency == "Lãnh lãi theo quý":
        period_months = 3
    else:  # Cuối kỳ
        period_months = term

    # Xử lý tính toán
    if principal > 0 and term > 0 and interest_rate > 0:
        rate_decimal = interest_rate / 100
        n_periods = term // period_months  # Số kỳ nguyên
        residual_months = term % period_months  # Số tháng lẻ còn lại
        
        rate_per_period = rate_decimal * (period_months / 12)
        
        if interest_type == "Lãi đơn":
            # Tính lãi đơn
            periodic_interest = principal * rate_per_period
            total_interest = periodic_interest * n_periods
            
            # Cộng thêm lãi của các tháng lẻ (nếu có)
            if residual_months > 0:
                total_interest += principal * rate_decimal * (residual_months / 12)
                
            total_amount = principal + total_interest
            
            # Hiển thị số liệu
            st.metric("Tổng số tiền gốc đã gửi", f"{principal:,.0f} VNĐ")
            st.metric("Tổng tiền lãi nhận được", f"{total_interest:,.0f} VNĐ")
            st.metric("Tổng số tiền gốc và lãi", f"{total_amount:,.0f} VNĐ", delta="Cuối kỳ")
            
            if frequency != "Lãnh lãi cuối kỳ":
                st.info(f"💡 **Tiền lãi định kỳ (mỗi {period_months} tháng):** {periodic_interest:,.0f} VNĐ")
                if residual_months > 0:
                    st.warning(f"Lưu ý: Có {residual_months} tháng lẻ cuối kỳ được tính lãi theo số ngày thực tế tương đương mức {principal * rate_decimal * (residual_months / 12):,.0f} VNĐ.")
        
        else:
            # Tính lãi kép
            current_principal = principal
            total_interest = 0
            schedule = []
            
            # Tính cho từng kỳ
            for i in range(1, n_periods + 1):
                interest_this_period = current_principal * rate_per_period
                current_principal += interest_this_period
                total_interest += interest_this_period
                
                schedule.append({
                    "Kỳ thứ": f"Kỳ {i} ({period_months} tháng)",
                    "Gốc đầu kỳ (VNĐ)": round(current_principal - interest_this_period),
                    "Lãi phát sinh (VNĐ)": round(interest_this_period),
                    "Gốc lũy kế (VNĐ)": round(current_principal)
                })
            
            # Tính cho các tháng lẻ cuối cùng (nếu có)
            if residual_months > 0:
                interest_this_period = current_principal * rate_decimal * (residual_months / 12)
                current_principal += interest_this_period
                total_interest += interest_this_period
                
                schedule.append({
                    "Kỳ thứ": f"Kỳ lẻ cuối ({residual_months} tháng)",
                    "Gốc đầu kỳ (VNĐ)": round(current_principal - interest_this_period),
                    "Lãi phát sinh (VNĐ)": round(interest_this_period),
                    "Gốc lũy kế (VNĐ)": round(current_principal)
                })
                
            total_amount = current_principal
            
            # Hiển thị số liệu
            st.metric("Tổng số tiền gốc ban đầu", f"{principal:,.0f} VNĐ")
            st.metric("Tổng tiền lãi cộng dồn", f"{total_interest:,.0f} VNĐ")
            st.metric("Tổng số tiền gốc và lãi", f"{total_amount:,.0f} VNĐ", delta="Cuối kỳ")
            
            st.info("💡 **Tiền lãi định kỳ:** Thay đổi tăng dần qua mỗi kỳ do tiền lãi được nhập vào gốc (Xem bảng chi tiết bên dưới).")
            
            # Hiển thị bảng chi tiết các kỳ đối với Lãi kép
            if len(schedule) > 0:
                st.markdown("### Bảng chi tiết sinh lời theo từng kỳ")
                df = pd.DataFrame(schedule)
                # Định dạng số có dấu phẩy
                st.dataframe(df.style.format({
                    "Gốc đầu kỳ (VNĐ)": "{:,.0f}",
                    "Lãi phát sinh (VNĐ)": "{:,.0f}",
                    "Gốc lũy kế (VNĐ)": "{:,.0f}"
                }), use_container_width=True)

    else:
        st.warning("Vui lòng nhập Số tiền gửi, Kỳ hạn và Lãi suất lớn hơn 0 để xem kết quả.")
