import streamlit  as st
from  data.v22.src.static.agyw import AgywPrev,AgywPrevCommune

_datim = AgywPrev()
st.cache(lambda _: _datim)

st.set_page_config(layout="wide")


st.header('Dreams Application Test')
st.subheader("Let\'s expose the indicator")

col1, col2 = st.columns(2)


col1.markdown(f"# {_datim.who_am_i} ")
col1.write(_datim.datim_titleI())
col1.dataframe(_datim.datim_agyw_prevI())
col1.write(_datim.datim_titleII())
col1.write(_datim.datim_agyw_prevII())
col1.write(_datim.datim_titleIII())
col1.write(_datim.datim_agyw_prevIII())
col1.write(_datim.datim_titleIV())
col1.write(_datim.datim_agyw_prevIV())


col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.write(_datim.total_datimI)
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.write(_datim.total_datimII)
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.write(_datim.total_datimIII)
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.markdown('#')
col2.write(_datim.total_datimIV)










