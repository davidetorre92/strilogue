import streamlit as st
from utils import *

st.set_page_config(page_title="ZDoom Dialogue Tool", layout="wide")

st.title("Universal Strife Dialogue conversation script compiler (Prototype 1)")
st.caption("Convert universal Strife dialog format into plain readable format")

st.info("**Disclaimer:** This tool is a prototype. The output should be thoroughly tested before being implemented directly into ZDoom projects.")

st.markdown("Paste your **dialogue script** below:")

# --- Language File Upload/Paste (Sidebar) ---
st.sidebar.header("🌍 Language File Variables")

# 1. File Uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload LANGUAGE File (or similar text file)",
    type=['txt', 'lan'],
    accept_multiple_files=False
)

language_text = ""
if uploaded_file is not None:
    # Read file content
    language_text = uploaded_file.read().decode("utf-8")
    st.sidebar.success("File uploaded!")
    
# 2. Text Area for direct paste
manual_text = st.sidebar.text_area(
    "Or paste variables here:",
    height=200,
    value=language_text # Pre-fill if a file was uploaded
)

# Use the manually pasted text if available, otherwise use file content
final_language_text = manual_text if manual_text else language_text

# 3. Parse and Display Variables
language_dict = {}
if final_language_text.strip():
    language_dict = parse_language_file(final_language_text)
    
    if language_dict:
        st.sidebar.subheader(f"Total Variables: {len(language_dict)}")
        # Display the dictionary for reference
        st.sidebar.json(language_dict)
    else:
        st.sidebar.info("Paste variables in the format: KEY = \"Value\"")

# --- End of Sidebar Code ---

# --- Text input area
zd_text = st.text_area("ZDoom dialogue input", height=400, placeholder="Paste your 'conversation { ... }' block here")

# --- New Conversion Option ---
st.markdown("---")
# Set a default state for the checkbox
if 'substitute_vars' not in st.session_state:
    st.session_state.substitute_vars = False

st.session_state.substitute_vars = st.checkbox(
    "Substitute Dialogue Variables (e.g., '$TXT_ID' becomes 'Dialogue Text')",
    value=st.session_state.substitute_vars
)

# --- Run conversion (UPDATED)
if st.button("Convert to Plain Text"):
    if zd_text.strip():
        # 1. Parse Dialogue
        parsed = parse_zdoom_dialogue(zd_text)
        
        # 2. Export (passing the new parameters)
        plain = to_plain_text(
            parsed, 
            st.session_state.substitute_vars, 
            language_dict # This dictionary is defined in the sidebar code
        )
        
        st.subheader("Plain Text Output")
        st.text_area("Plain Output", plain, height=400)
    else:
        st.warning("Please paste a ZDoom dialogue block first.")

st.markdown("---")
st.header("Reverse Conversion: Plain Text to ZDoom Format")
plain_input_reverse = st.text_area("Paste Plain Text here for ZDoom conversion", height=400, placeholder="Paste your plain text dialogue (starting with #NAME, #Page, etc.)")
# Optional: Let the user specify the main actor name for the ZDoom output
actor_input = st.text_input("Specify Actor Class Name", value="NewActorName")


# --- New Conversion Option for ZDoom Output ---
if 'literal_output' not in st.session_state:
    st.session_state.literal_output = False

st.session_state.literal_output = st.checkbox(
    "Literal Text Output Mode (Substitute all variables with full dialogue string)",
    value=st.session_state.literal_output,
    help="When checked, $TXT_IDs will be replaced by their corresponding text (e.g., \$TXT_ID becomes \"Hello dear!\"). Requires variables to be parsed in the sidebar."
)

if st.button("Convert to ZDoom Dialogue Script"):
    if plain_input_reverse.strip():
        try:
            print()
            print()
            # 1. Parse the Plain Text input
            parsed_reverse = parse_plain_text(plain_input_reverse)
            # 2. Generate the ZDoom Text (NOW PASSING NEW PARAMETERS)
            zdoom_output = to_zdoom_text(
                parsed_reverse, 
                actor_name=actor_input, 
                literal_output=st.session_state.literal_output, 
                language_dict=language_dict # The dictionary parsed from the sidebar
            )
            
            st.subheader("💻 ZDoom Dialogue Script Output")
            st.code(zdoom_output, language='c')


            # Add a download button for the generated file
            st.download_button(
                label="Download ZDoom Script",
                data=zdoom_output,
                file_name="dialogue_script.txt",
                mime="text/plain"
            )

            if not st.session_state.literal_output:
                language_snippet = generate_language_snippet(parsed_reverse)
                
                st.markdown("---")
                st.subheader("🌐 Language File Snippet")
                st.caption("Use this output to update your external LANGUAGE file.")
                
                st.text_area("Language Variables", language_snippet, height=200)

                # Add a download button for the generated file
                st.download_button(
                    label="Download Language Snippet",
                    data=language_snippet,
                    file_name="dialogue_language_snippet.txt",
                    mime="text/plain"
                )


        except Exception as e:
            st.error(f"An error occurred during reverse conversion. Please check your plain text format.")
            st.exception(e) # Show detailed error for debugging
    else:
        st.warning("Please paste the plain text dialogue above.")