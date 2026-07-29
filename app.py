import streamlit as st

st.set_page_config(
    page_title="CrisisConnect UK",
    page_icon="🤝",
    layout="wide"
)

st.title("🤝 CrisisConnect UK")
st.subheader("Free food support — get help in minutes, not days")

st.markdown("""
---
### The problem we're solving
Right now if you need food urgently in the UK you have to:
- Know who to call
- Get through on the phone
- Explain your crisis to a stranger
- Wait for a paper voucher
- Then travel to a food bank

**That's too many steps when you're hungry today.**

CrisisConnect UK replaces that entire process with a simple online form.
No phone calls. No waiting. Get a digital voucher instantly.

---
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("### 🔍 Step 1\n**Find your nearest food bank**\nSee what's available near you and whether you need a referral.")

with col2:
    st.success("### 📝 Step 2\n**Fill a simple form**\nTell us your postcode and household needs. Takes 2 minutes.")

with col3:
    st.warning("### 🎫 Step 3\n**Get your digital voucher**\nInstant QR code voucher. Show it at the food bank or request delivery.")

st.markdown("---")
st.markdown("👈 **Use the menu on the left to get started**")

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Food Banks in Database", "1,972")
col2.metric("UK Households in Food Crisis", "1 in 10")
col3.metric("Steps to Get Help Today", "3")

st.divider()
st.caption("CrisisConnect UK | Free & Open Source | Built by Shikha Agarwal | Data from Give Food API")