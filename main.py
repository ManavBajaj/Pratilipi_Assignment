import streamlit as st
import json
import os
from datetime import datetime
from extractor import extract_signals
from adjudicator import decide_subgenre, load_taxonomy

# Page config
st.set_page_config(
    page_title="Adaptive Taxonomy Mapper",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .signal-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .unmapped-badge {
        background-color: #ffc107;
        color: black;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Adaptive Taxonomy Mapper</div>', unsafe_allow_html=True)

# Sidebar - API Configuration
with st.sidebar:
    st.header("Configuration")
    
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Get free API key from https://console.groq.com/"
    )
    
    if api_key:
        st.session_state.api_configured = True
        st.success("API Key configured")
    else:
        st.warning("Enter API key to use LLM")
    
    st.divider()
    
    if st.button("Start New Session", type="primary"):
        st.session_state.results = []
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.rerun()
    
    st.divider()
    
    # Taxonomy viewer
    with st.expander("View Taxonomy"):
        try:
            taxonomy, _ = load_taxonomy()
            st.json(taxonomy)
        except:
            st.error("taxonomy.json not found")

# Main content
tab1, tab2, tab3 = st.tabs(["Map Story", "Session Results", "Test Cases"])

# TAB 1: Map Story
with tab1:
    st.header("Map a Story to Taxonomy")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        story_input = st.text_area(
            "Story Description",
            height=150,
            placeholder="Enter the story description or snippet here...",
            help="Paste the story text you want to classify"
        )
    
    with col2:
        tags_input = st.text_input(
            "User Tags (comma-separated)",
            placeholder="Love, Action, Scary",
            help="Enter tags separated by commas"
        )
        
        st.write("")
        st.write("")
        
        map_button = st.button("Map to Taxonomy", type="primary", use_container_width=True)
    
    if map_button:
        if not story_input.strip():
            st.error("Please enter a story description")
        elif not st.session_state.api_configured:
            st.error("Please configure API key in the sidebar")
        else:
            with st.spinner("Analyzing story..."):
                # Parse tags
                tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                
                try:
                    # Extract signals
                    signals = extract_signals(api_key, story_input, tags, api_type="groq")
                    
                    # Decide subgenre
                    decision = decide_subgenre(signals, story_input, tags)
                    
                    # Store result
                    result = {
                        "id": len(st.session_state.results) + 1,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "story": story_input,
                        "tags": tags,
                        "signals": signals,
                        "decision": decision
                    }
                    st.session_state.results.append(result)
                    
                    # Display result
                    st.success("Analysis Complete")
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    
                    # Decision
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader("Classification Result")
                        if decision['subgenre'] == "[UNMAPPED]":
                            st.markdown(f'<span class="unmapped-badge">{decision["subgenre"]}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span class="success-badge">{decision["subgenre"]}</span>', unsafe_allow_html=True)
                        
                        if decision['parent']:
                            st.write(f"**Category Path:** {decision['parent']}")
                    
                    with col2:
                        st.metric("Result ID", f"#{result['id']}")
                    
                    # Reasoning
                    st.write("**Reasoning:**")
                    st.info(decision['reasoning'])
                    
                    # Signals
                    with st.expander("Extracted Signals", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            for i, (key, value) in enumerate(list(signals.items())[:5]):
                                st.write(f"**{key.replace('_', ' ').title()}:** `{value}`")
                        with col2:
                            for key, value in list(signals.items())[5:]:
                                st.write(f"**{key.replace('_', ' ').title()}:** `{value}`")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 2: Session Results
with tab2:
    st.header("Session Results")
    
    if not st.session_state.results:
        st.info("No results yet. Map some stories in the 'Map Story' tab!")
    else:
        # Stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Total Mapped", len(st.session_state.results))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            mapped_count = sum(1 for r in st.session_state.results if r['decision']['subgenre'] != "[UNMAPPED]")
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Successfully Mapped", mapped_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            unmapped_count = sum(1 for r in st.session_state.results if r['decision']['subgenre'] == "[UNMAPPED]")
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Unmapped", unmapped_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Download button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            results_json = json.dumps(st.session_state.results, indent=2)
            st.download_button(
                label="Download Results (JSON)",
                data=results_json,
                file_name=f"taxonomy_results_{st.session_state.session_id}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.divider()
        
        # Results list
        st.subheader("All Results")
        
        for result in reversed(st.session_state.results):
            with st.expander(f"Result #{result['id']} - {result['decision']['subgenre']} ({result['timestamp']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Story:**")
                    st.write(result['story'])
                    
                    if result['tags']:
                        st.write(f"**Tags:** {', '.join(result['tags'])}")
                
                with col2:
                    st.write("**Classification:**")
                    if result['decision']['subgenre'] == "[UNMAPPED]":
                        st.markdown(f'<span class="unmapped-badge">{result["decision"]["subgenre"]}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="success-badge">{result["decision"]["subgenre"]}</span>', unsafe_allow_html=True)
                    
                    if result['decision']['parent']:
                        st.write(f"**Path:** {result['decision']['parent']}")
                
                st.write("**Reasoning:**")
                st.info(result['decision']['reasoning'])
                
                with st.expander("View Signals"):
                    st.json(result['signals'])

# TAB 3: Test Cases
# TAB 3: Test Cases
with tab3:
    st.header("Golden Test Cases")
    st.write("Run all 10 test cases from the assignment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        run_tests = st.button("Run All Test Cases", type="primary", use_container_width=True)
    
    with col2:
        try:
            with open("test_cases.json") as f:
                test_cases_data = f.read()
            st.download_button(
                label="Download Test Cases (JSON)",
                data=test_cases_data,
                file_name="test_cases.json",
                mime="application/json",
                use_container_width=True
            )
        except FileNotFoundError:
            st.button("Download Test Cases (JSON)", disabled=True, use_container_width=True)
            st.caption("test_cases.json not found")
    
    # Now handle the test execution outside the columns
    if run_tests:
        if not st.session_state.api_configured:
            st.error("Please configure API key in the sidebar")
        else:
            try:
                with open("test_cases.json") as f:
                    test_cases = json.load(f)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                test_results = []
                
                for i, case in enumerate(test_cases):
                    status_text.text(f"Processing case {i+1}/{len(test_cases)}...")
                    
                    try:
                        signals = extract_signals(api_key, case['story'], case['tags'], api_type="groq")
                        
                        decision = decide_subgenre(signals, case['story'], case['tags'])
                        
                        test_results.append({
                            "id": case['id'],
                            "tags": case['tags'],
                            "story": case['story'],
                            "expected": case['expected'],
                            "actual": decision['subgenre'],
                            "signals": signals,
                            "decision": decision,
                            "match": decision['subgenre'].lower() in case['expected'].lower() or case['expected'].lower() in decision['subgenre'].lower()
                        })
                    except Exception as e:
                        st.error(f"Error processing case {case['id']}: {str(e)}")
                    
                    progress_bar.progress((i + 1) / len(test_cases))
                
                status_text.text("All test cases completed")
                
                # Show results
                st.divider()
                
                matches = sum(1 for r in test_results if r['match'])
                st.success(f"**Accuracy: {matches}/{len(test_results)} ({matches/len(test_results)*100:.1f}%)**")
                
                st.divider()
                
                for result in test_results:
                    match_icon = "[PASS]" if result['match'] else "[FAIL]"
                    
                    with st.expander(f"{match_icon} Case {result['id']} - Expected: {result['expected']} | Got: {result['actual']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Story:**")
                            st.write(result['story'])
                            st.write(f"**Tags:** {', '.join(result['tags'])}")
                        
                        with col2:
                            st.write("**Expected:**")
                            st.code(result['expected'])
                            st.write("**Actual:**")
                            st.code(result['actual'])
                        
                        st.write("**Reasoning:**")
                        st.info(result['decision']['reasoning'])
                        
                        with st.expander("View Signals"):
                            st.json(result['signals'])
                
            except FileNotFoundError:
                st.error("test_cases.json not found. Please create it first.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>Adaptive Taxonomy Mapper | Session: {}</small>
</div>
""".format(st.session_state.session_id), unsafe_allow_html=True)