import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
st.header('st.write')
st.write('Hello,*World!*:sunglasses')
st.write(1234)
df=pd.DataFrame({
    '첫번째 칼럼':[1,2,3,4],
    '두번째 칼럼':[10,20,30,40]
    })
st.write(df)
st.write('아래는 DataFrame입니다.',df,'위는 dataframe입니다.')
df2=pd.DataFrame(
    np.random.randn(200,3),
    columns=['a','b','c'])
c=alt.Chart(df2).mark_circle().encode(
    x='a',y='b',color='c',tooltip=['a','b','c'])
st.write(c)