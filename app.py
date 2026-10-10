import json
from datetime import date
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from expense_agent import ExpenseAgent, load_expenses, save_expenses, DEFAULT_BUDGETS, CATEGORIES

st.set_page_config(page_title="SpendSmart | Expense Agent", page_icon="💸", layout="wide")
st.markdown(r'''<style>
.stApp{background:radial-gradient(ellipse at top left,rgba(91,60,160,.16),transparent 35%),radial-gradient(ellipse at top right,rgba(20,150,170,.08),transparent 32%),#0b0d12;color:#eef2ff}
[data-testid="stHeader"]{background:rgba(11,13,18,.85)} [data-testid="stSidebar"]{background:#10131b;border-right:1px solid #242938}
[data-testid="stSidebar"] *{color:#e5e9f5}.block-container{max-width:1280px;padding-top:1.5rem;padding-bottom:2.5rem}
.hero{padding:1.55rem 1.8rem;border-radius:20px;color:#f8fafc;background:linear-gradient(115deg,#171329,#171d34 55%,#102b31);border:1px solid #34314f;box-shadow:0 14px 40px #0005;margin-bottom:1.2rem}
.hero h1{color:#f8fafc!important;margin:0;font-size:2.25rem;letter-spacing:-.04em}.hero p{color:#b7c2d8!important;margin:.5rem 0 0;font-size:1rem}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#171c27,#121620);border:1px solid #2a3040;padding:16px 18px;border-radius:16px;box-shadow:0 8px 24px #0002}
div[data-testid="stMetric"] label{color:#aab4c9!important}div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#f4f6ff!important}
div[data-testid="stTabs"] [role="tablist"]{gap:.35rem;border-bottom:1px solid #2a3040}div[data-testid="stTabs"] button{color:#aab4c9!important;border-radius:10px 10px 0 0;font-weight:650}div[data-testid="stTabs"] button[aria-selected="true"]{color:#c4b5fd!important;border-bottom-color:#8b5cf6!important}
div.stButton>button,div.stFormSubmitButton>button,div[data-testid="stDownloadButton"] button{background:#1a2030;color:#edf0ff;border:1px solid #353d52;border-radius:11px;font-weight:650}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{border-color:#8b5cf6;color:#ddd6fe;background:#24203a}div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(100deg,#7c3aed,#4f46e5);color:white;border:0}
.stTextInput input,.stNumberInput input,.stDateInput input{background:#121722!important;color:#eef2ff!important;border-color:#343b4e!important;border-radius:10px!important}div[data-baseweb="select"]>div{background:#121722!important;border-color:#343b4e!important;border-radius:10px!important}div[data-baseweb="select"] *{color:#eef2ff!important}
div[data-baseweb="popover"],div[role="listbox"],ul[role="listbox"],div[role="option"]{background:#171c27!important;color:#eef2ff!important}div[role="option"]:hover{background:#29243e!important}
.stMarkdown,p,label,h1,h2,h3,h4,li{color:#e7ebf6}[data-testid="stCaptionContainer"],.small-muted{color:#98a2b8!important}.panel{background:linear-gradient(145deg,#171c27,#121620);border:1px solid #2a3040;padding:1.1rem 1.25rem;border-radius:16px;color:#e7ebf6}
div[data-testid="stDataFrame"]{border:1px solid #2a3040;border-radius:12px;overflow:hidden}
.budget-track{width:100%;height:14px;background:#303747;border-radius:999px;overflow:hidden;margin:8px 0 14px 0;border:1px solid #424b5e}
.budget-fill{height:100%;border-radius:999px;transition:width .25s ease}
.budget-fill.snapshot{background:#22c55e}
.budget-fill.category{background:#3b82f6}
.budget-fill.warning{background:#f59e0b}
.budget-fill.over{background:#ef4444}
.budget-pct{font-size:.9rem;color:#cbd5e1;margin-left:6px}
div[data-testid="stAlert"]{background:#171c27;border:1px solid #343b4e;color:#e7ebf6}hr{border-color:#2a3040!important}
</style><div class="hero"><h1>💸 SpendSmart Agent</h1><p>Your personal spending agent — plan your money, monitor budgets, and get a clear next action.</p></div>''', unsafe_allow_html=True)

BUDGET_FILE=Path('budgets.json'); FINANCE_FILE=Path('monthly_finance.json')
def money(x): return f"₹{float(x):,.2f}"
def read_json(path,default):
    try: return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default
    except (json.JSONDecodeError,OSError): return default
def write_json(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def month_key(d):
    try: return pd.to_datetime(d,errors='coerce').strftime('%Y-%m')
    except Exception: return 'NaT'
def all_data(): return load_expenses()
def get_month_items(month): return [x for x in all_data() if month_key(x.get('date',''))==month]
def finance_map():
    x=read_json(FINANCE_FILE,{})
    return x if isinstance(x,dict) else {}
def finance_for(month): return finance_map().get(month,{'income':0.0,'investments':0.0,'savings':0.0})

budgets={**DEFAULT_BUDGETS,**read_json(BUDGET_FILE,{})}
items=all_data(); months=sorted({month_key(x.get('date','')) for x in items if month_key(x.get('date',''))!='NaT'},reverse=True)
this_month=date.today().strftime('%Y-%m')
if this_month not in months: months.insert(0,this_month)
with st.sidebar:
    st.markdown('## 🗓️ Reporting month')
    selected_month=st.selectbox('Choose month',months,index=0)
    fin=finance_for(selected_month)
    st.divider(); st.markdown('## 💰 Monthly money plan')
    st.caption('Monthly income is your overall limit. Record investments and savings for this month.')
    with st.form('finance_form'):
        income_input=st.number_input('Monthly income (₹)',min_value=0.0,value=float(fin.get('income',0)),step=1000.0)
        investments_input=st.number_input('Monthly investments (₹)',min_value=0.0,value=float(fin.get('investments',0)),step=500.0)
        savings_input=st.number_input('Monthly savings (₹)',min_value=0.0,value=float(fin.get('savings',0)),step=500.0)
        finance_saved=st.form_submit_button('Save money plan',use_container_width=True)
    if finance_saved:
        fm=finance_map(); fm[selected_month]={'income':income_input,'investments':investments_input,'savings':savings_input}; write_json(FINANCE_FILE,fm); st.toast('Monthly money plan saved.'); st.rerun()
    fin=finance_for(selected_month)
    if fin['investments']+fin['savings']>fin['income']: st.warning('Investments + savings exceed income.')
    st.divider(); st.markdown('## 🎯 Category limits')
    st.caption('Category limits sit within your overall monthly income limit.')
    new_budgets={}
    for cat in CATEGORIES: new_budgets[cat]=st.number_input(cat,min_value=0,value=int(budgets.get(cat,0)),step=500,key=f'budget_{cat}')
    if st.button('💾 Save category limits',use_container_width=True): write_json(BUDGET_FILE,new_budgets); st.toast('Category limits saved.'); st.rerun()
    budgets={**DEFAULT_BUDGETS,**read_json(BUDGET_FILE,{})}

tab_overview,tab_add,tab_agent,tab_data=st.tabs(['✨ Overview','➕ Add expense','🤖 Agent cockpit','📁 Transactions'])
with tab_add:
    st.markdown('### Add a transaction')
    st.markdown('<div class="small-muted">Choose the category yourself. The agent preserves your selection.</div>',unsafe_allow_html=True)
    with st.form('add_expense_form',clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            expense_date=st.date_input('Expense date',value=date.today()); description=st.text_input('What did you spend on?',placeholder='e.g., lunch at college canteen'); category=st.selectbox('Category',CATEGORIES)
        with c2:
            amount=st.number_input('Amount (₹)',min_value=.01,value=100.0,step=50.0); payment_method=st.selectbox('Payment method',['UPI','Cash','Debit card','Credit card','Bank transfer','Other']); notes=st.text_input('Optional note',placeholder='e.g., weekly groceries')
        submitted=st.form_submit_button('＋ Save expense',type='primary',use_container_width=True)
        if submitted:
            if not description.strip(): st.error('Please enter a description.')
            else:
                current=all_data(); current.append({'id':max([int(x.get('id',0)) for x in current],default=0)+1,'date':expense_date.isoformat(),'description':description.strip(),'amount':round(float(amount),2),'category':category,'category_source':'user','payment_method':payment_method,'notes':notes.strip()}); save_expenses(current); st.success(f'Saved {money(amount)} under {category}.'); st.rerun()

with tab_overview:
    month_items=get_month_items(selected_month); fin=finance_for(selected_month); income=float(fin.get('income',0)); investments=float(fin.get('investments',0)); savings=float(fin.get('savings',0)); spending=round(sum(float(x.get('amount',0)) for x in month_items),2); remaining=round(income-spending-investments-savings,2)
    st.markdown(f'### Your money at a glance · {selected_month}')
    a,b,c,d=st.columns(4); a.metric('💵 Monthly income',money(income)); b.metric('💸 Spending',money(spending)); c.metric('📈 Investments',money(investments)); d.metric('🏦 Savings',money(savings))
    if income>0:
        if remaining>=0: st.caption(f'{money(remaining)} remains unallocated from this month’s income.')
        else: st.error(f'Spending, investments, and savings exceed income by {money(abs(remaining))}.')
    else: st.info('Enter monthly income in the sidebar to set the overall monthly limit.')
    chart_col,info_col=st.columns([1.05,1])
    with chart_col:
        st.markdown('#### Income allocation')
        if income>0:
            unspent=max(income-spending-investments-savings,0.0)
            over_allocated=max(spending+investments+savings-income,0.0)
            pie=pd.DataFrame([
                {'Type':'Spending','Amount':spending},
                {'Type':'Investments','Amount':investments},
                {'Type':'Savings','Amount':savings},
                {'Type':'Unallocated income','Amount':unspent},
            ])
            if over_allocated>0:
                st.warning(f'Your spending, investments, and savings exceed monthly income by {money(over_allocated)}. The pie chart shows income allocation up to your total income.')
            fig=px.pie(pie,names='Type',values='Amount',hole=.48,color='Type',color_discrete_map={'Spending':'#8B5CF6','Investments':'#22D3EE','Savings':'#34D399','Unallocated income':'#64748B'})
            fig.update_traces(textposition='inside',texttemplate='%{label}<br>%{percent}',textfont_color='#F4F6FF',marker_line_color='#131720',marker_line_width=3)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#E7EBF6',legend=dict(font=dict(color='#E7EBF6')),margin=dict(t=12,b=12,l=8,r=8))
            st.plotly_chart(fig,use_container_width=True); st.caption('Each slice is shown as a percentage of total monthly income. “Unallocated income” is income not yet spent, invested, or saved.')
        else:
            st.info('Enter monthly income in the sidebar to show allocation as percentages of total income.')
    with info_col:
        st.markdown('#### Category spending')
        if month_items:
            category_totals=pd.DataFrame(month_items).groupby('category')['amount'].sum().sort_values(ascending=False)
            st.bar_chart(category_totals,color='#8B5CF6',height=420)
        else: st.caption('No expenses recorded for this month yet.')
    st.markdown('#### Category budget progress')
    by_cat=pd.DataFrame(month_items).groupby('category')['amount'].sum().to_dict() if month_items else {}
    for cat in CATEGORIES:
        spent_cat=float(by_cat.get(cat,0)); limit=float(budgets.get(cat,0))
        # Correct ratio: a spend of 2,500 against a limit of 5,000 fills exactly half the bar.
        denominator=limit if limit>0 else income
        ratio=min(max(spent_cat/denominator,0),1) if denominator>0 else 0
        label=f'{cat}: {money(spent_cat)} / {money(limit)}' if limit>0 else f'{cat}: {money(spent_cat)} / income {money(income)}'
        st.markdown(f'<div>{label}<span class="budget-pct">{ratio*100:.0f}%</span></div>',unsafe_allow_html=True)
        if limit>0 and spent_cat>limit: fill_class='over'
        elif limit>0 and ratio>=.8: fill_class='warning'
        else: fill_class='category'
        st.markdown(f'<div class="budget-track"><div class="budget-fill {fill_class}" style="width:{ratio*100:.2f}%"></div></div>',unsafe_allow_html=True)
        if limit>0 and spent_cat>limit: st.caption(f'Over category limit by {money(spent_cat-limit)}')

with tab_agent:
    st.markdown(f'### Agent cockpit · {selected_month}')
    st.write('The agent reviews only transactions from the selected month. It plans, evaluates risks, chooses a next action, and checks its calculations.')
    st.markdown('<div class="panel"><b>Agent loop</b><br>1. <b>Plan:</b> prepare ordered checks.<br>2. <b>Act:</b> validate selected-month transactions and fill missing categories only.<br>3. <b>Evaluate:</b> compare category spending with limits and total spending with monthly income.<br>4. <b>Decide:</b> prioritize budget risks and choose a concrete next action.<br>5. <b>Self-check:</b> verify totals and category coverage.</div>',unsafe_allow_html=True)
    rcol,ccol=st.columns(2)
    with rcol: run_agent=st.button('🚀 Run agent for selected month',type='primary',use_container_width=True)
    with ccol:
        if st.button('↻ Clear previous run',use_container_width=True): st.session_state.pop('agent_result',None); st.session_state.pop('agent_result_month',None); st.rerun()
    if run_agent:
        selected_items=get_month_items(selected_month); month_budgets=dict(budgets); month_budgets['__monthly_income__']=float(finance_for(selected_month).get('income',0)); month_budgets['__investments__']=float(finance_for(selected_month).get('investments',0)); month_budgets['__savings__']=float(finance_for(selected_month).get('savings',0))
        result=ExpenseAgent(month_budgets).run(selected_items)
        # Only write category updates back to matching selected-month rows; all other months remain unchanged.
        result_by_id={str(x.get('id')):x for x in result['expenses']}; all_items=all_data(); updated=[]
        for item in all_items:
            if month_key(item.get('date',''))==selected_month and str(item.get('id')) in result_by_id: updated.append(result_by_id[str(item.get('id'))])
            else: updated.append(item)
        save_expenses(updated); st.session_state['agent_result']=result; st.session_state['agent_result_month']=selected_month
    result=st.session_state.get('agent_result'); result_month=st.session_state.get('agent_result_month')
    if result and result_month==selected_month:
        s=result['summary']; k1,k2,k3,k4=st.columns(4); k1.metric('Transactions reviewed',s['transactions_processed']); k2.metric('Month’s spending',money(s['total_spending'])); k3.metric('Over-budget categories',s['over_budget_categories']); k4.metric('Self-check','PASSED' if s['self_evaluation_passed'] else 'CHECK')
        # Explicit overall monthly income-cap assessment.
        current_fin=finance_for(selected_month); monthly_cap=float(current_fin.get('income',0)); total_alloc=s['total_spending']+float(current_fin.get('investments',0))+float(current_fin.get('savings',0))
        st.markdown('#### 🎯 Agent’s chosen next action')
        if monthly_cap>0 and total_alloc>monthly_cap: st.warning(f'Monthly income limit exceeded by {money(total_alloc-monthly_cap)}. Review spending or planned allocations.')
        st.info(result['next_action'])
        st.markdown('#### 🚦 Budget risks')
        if result['risk_assessment']:
            for risk in result['risk_assessment']: st.warning(risk)
        else: st.success('No category is over its configured limit in this month’s transactions.')
        if monthly_cap>0: st.write(f'**Monthly income cap check:** {money(total_alloc)} allocated of {money(monthly_cap)} income ({total_alloc/monthly_cap*100:.1f}%).')
        st.markdown('#### 🧠 Recommendations')
        for recommendation in result['recommendations']: st.write(f'- {recommendation}')
        st.markdown('#### 🧪 Self-evaluation checks')
        for name,passed in result['self_evaluation'].items(): st.write(f"{'✅' if passed else '❌'} {name.replace('_',' ').title()}")
        st.markdown('#### 🔍 Execution trace'); st.dataframe(pd.DataFrame(result['trace']),use_container_width=True,hide_index=True)
        st.download_button('⬇ Download agent report (JSON)',data=json.dumps(result,indent=2,ensure_ascii=False),file_name=f'spendsmart_report_{selected_month}.json',mime='application/json')
    elif result and result_month!=selected_month: st.info('The previous run belongs to a different month. Run the agent again for this selected month.')
    else: st.info('Run the agent to see a month-specific risk assessment and next action.')

with tab_data:
    st.markdown('### Transaction manager'); current=all_data()
    if current:
        df=pd.DataFrame(current); st.dataframe(df,use_container_width=True,hide_index=True); st.caption('Correct categories below when needed, then save changes.')
        if 'category' not in df.columns: df['category']='Other'
        edited=st.data_editor(df,use_container_width=True,hide_index=True,disabled=[col for col in df.columns if col not in ('category','description','amount','payment_method','notes')],column_config={'category':st.column_config.SelectboxColumn('Category',options=CATEGORIES,required=True)},key='transaction_editor')
        if st.button('💾 Save transaction edits'): save_expenses(edited.to_dict(orient='records')); st.success('Changes saved.'); st.rerun()
    else: st.info('No transactions yet.')
    c1,c2=st.columns(2)
    with c1:
        if st.button('✨ Load demo transactions'):
            demo=[{'id':1,'date':date.today().replace(day=2).isoformat(),'description':'Grocery supermarket','amount':1250.0,'category':'Food','category_source':'user','payment_method':'UPI','notes':'Weekly groceries'},{'id':2,'date':date.today().replace(day=3).isoformat(),'description':'Bus and metro travel','amount':420.0,'category':'Transport','category_source':'user','payment_method':'Cash','notes':''},{'id':3,'date':date.today().replace(day=4).isoformat(),'description':'Movie tickets','amount':2850.0,'category':'Entertainment','category_source':'user','payment_method':'Credit card','notes':'Weekend outing'},{'id':4,'date':date.today().replace(day=5).isoformat(),'description':'Electricity bill','amount':1600.0,'category':'Bills','category_source':'user','payment_method':'Bank transfer','notes':''},{'id':5,'date':date.today().replace(day=6).isoformat(),'description':'Online shopping shoes','amount':3100.0,'category':'Shopping','category_source':'user','payment_method':'UPI','notes':''},{'id':6,'date':date.today().replace(day=7).isoformat(),'description':'Pharmacy medicine','amount':520.0,'category':'Health','category_source':'user','payment_method':'Debit card','notes':''}]
            save_expenses(demo); st.success('Demo transactions loaded.'); st.rerun()
    with c2:
        if st.button('🗑 Clear all transactions'): save_expenses([]); st.session_state.pop('agent_result',None); st.session_state.pop('agent_result_month',None); st.warning('All local transactions cleared.'); st.rerun()
