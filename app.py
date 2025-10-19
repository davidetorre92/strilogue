import streamlit as st
import uuid
from typing import List, Dict

# Import our modules
from dialogue_models import DialoguePage
from dialogue_parsers import DialogueParser
from usdf_converter import USDFConverter
from graphviz_generator import GraphvizGenerator
from variable_manager import VariableManager
from default_content import DEFAULT_ZDOOM_EXAMPLE, DEFAULT_PLAIN_TEXT_EXAMPLE

class DialogueEditorApp:
    """Main application class for the dialogue editor"""
    
    def __init__(self):
        self.setup_session_state()
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Strilogue - ZDoom Dialogue Editor",
            page_icon="🎭",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def setup_editor_listeners(self):
        """Set up change detection for editors"""
        # Plain text editor change detection
        if 'plain_editor' in st.session_state:
            if st.session_state.plain_editor != st.session_state.plain_text:
                st.session_state.plain_text = st.session_state.plain_editor
                # st.session_state.last_modified = 'plain'
                # st.session_state.unsynced_changes = True
        
        # ZDoom editor change detection  
        if 'zdoom_editor' in st.session_state:
            if st.session_state.zdoom_editor != st.session_state.zdoom_text:
                st.session_state.zdoom_text = st.session_state.zdoom_editor
                # st.session_state.last_modified = 'zdoom'
                # st.session_state.unsynced_changes = True


    def setup_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'plain_text': DEFAULT_PLAIN_TEXT_EXAMPLE,
            'zdoom_text': DEFAULT_ZDOOM_EXAMPLE,
            'actor_name': "ChaingunGuy",
            'literal_output': False,
            'master_variables': {},
            'graphviz_source': "",
            'editor_key': str(uuid.uuid4()),
            'conflict_variables': {},
            'last_modified': 'plain',
            # Add these - initialize editor keys with the same values
            'plain_editor': DEFAULT_PLAIN_TEXT_EXAMPLE,
            'zdoom_editor': DEFAULT_ZDOOM_EXAMPLE
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


    def render_header(self):
        """Render the application header"""
        st.title("🎭 Strilogue - ZDoom/Strife Dialogue Editor")
        st.caption("Bidirectional editor for GZDoom dialogue with visual flow preview")
        st.markdown("---")
    
    def render_sidebar(self):
        """Render the sidebar with language file management"""
        st.sidebar.header("🌍 Language File Authority")
        
        # File upload
        uploaded_file = st.sidebar.file_uploader(
            "Upload LANGUAGE File", 
            type=['txt', 'lan'], 
            accept_multiple_files=False,
            help="Upload a ZDoom language file to provide variable definitions"
        )
        
        language_text = ""
        if uploaded_file is not None:
            language_text = uploaded_file.read().decode("utf-8")
            st.sidebar.success("📁 File uploaded successfully!")
        
        # Manual input
        manual_text = st.sidebar.text_area(
            "Or paste variables here:",
            height=200,
            value=language_text,
            help="Paste variables in KEY = \"Value\" format"
        )
        
        final_language_text = manual_text if manual_text else language_text
        
        # Parse language variables
        if final_language_text.strip():
            st.session_state.master_variables = VariableManager.parse_language_file(final_language_text)
        
        # Show active variables
        if st.session_state.master_variables:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Active Variable Definitions")
            st.sidebar.json(st.session_state.master_variables)
    
    def render_graph_preview(self):
        """Render the GraphViz visualization at the top"""
        st.subheader("📊 Dialogue Flow Preview")
        
        if st.session_state.graphviz_source:
            try:
                st.graphviz_chart(st.session_state.graphviz_source, width='stretch')
            except Exception as e:
                st.error(f"❌ Could not render graph: {e}")
                with st.expander("Show GraphViz Source"):
                    st.code(st.session_state.graphviz_source, language='text')
        else:
            st.info("👆 Sync editors to generate flow visualization")
        
        st.markdown("---")

    def sync_plain_to_zdoom(self):
        """Convert plain text to ZDoom format"""
        try:
            pages = DialogueParser.parse_plain_text(st.session_state.plain_text)
            if not pages:
                st.error("❌ No valid pages found in plain text. Please check your syntax.")
                return
            self.update_from_pages(pages)
            st.success("✅ Converted Plain Text to ZDoom Format!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Conversion failed: {str(e)}")
            with st.expander("Debug Info"):
                st.code(f"Plain text content:\n{st.session_state.plain_text}")

    def sync_zdoom_to_plain(self):
        """Convert ZDoom format to plain text"""
        try:
            pages = USDFConverter.parse_zdoom_dialogue(st.session_state.zdoom_text)
            if not pages:
                st.error("❌ No valid pages found in ZDoom text. Please check your syntax.")
                return
            self.update_from_pages(pages)
            st.success("✅ Converted ZDoom Format to Plain Text!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Conversion failed: {str(e)}")
            with st.expander("Debug Info"):
                st.code(f"ZDoom content:\n{st.session_state.zdoom_text}")

    def render_sync_buttons(self):
        """Render the bidirectional sync buttons between editors"""
        st.markdown("<br>" * 8, unsafe_allow_html=True)  # Vertical spacing
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("→", help="Convert Plain Text to ZDoom Format", use_container_width=True):
                self.sync_plain_to_zdoom()
        
        with col2:
            if st.button("←", help="Convert ZDoom Format to Plain Text", use_container_width=True):
                self.sync_zdoom_to_plain()


    def render_editor_controls(self):
        """Render editor controls below the sync buttons"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Actor Class Name",
                value=st.session_state.actor_name,
                key='actor_name_input',
                help="Class name for the conversation actor"
            )
        
        with col2:
            st.checkbox(
                "Literal Text Output",
                value=st.session_state.literal_output,
                key='literal_output_checkbox',
                help="Substitute variables with their text values"
            )
        
        # Show conflict resolution if needed
        if st.session_state.conflict_variables:
            self.render_conflict_resolution()
        
        st.markdown("---")

    def render_editors(self):
        """Render the bidirectional text editors with explicit sync buttons"""
        st.subheader("✍️ Dialogue Editors")
        
        col1, col2, col3 = st.columns([5, 1, 5])
        
        with col1:
            self.render_plain_text_editor()
        
        with col2:
            self.render_sync_buttons()
        
        with col3:
            self.render_zdoom_editor()
        
        self.render_editor_controls()

    def render_plain_text_editor(self):
        """Render the plain text editor"""
        st.markdown("**1. Plain Text Editor** 📝")
        st.caption("Primary editing interface. Use #tags for metadata and logic.")
        
        st.text_area(
            "Plain Dialogue",
            value=st.session_state.plain_text,
            height=400,
            key="plain_editor",  # This key is crucial
            label_visibility="collapsed",
            help="Edit dialogue in plain text format with #tags"
        )

    
    def render_zdoom_editor(self):
        """Render the ZDoom/USDF editor"""
        st.markdown("**2. ZDoom Script Editor** ⚙️")
        st.caption("Edit USDF directly. Changes require sync confirmation.")
        
        st.text_area(
            "ZDoom Dialogue", 
            value=st.session_state.zdoom_text,
            height=400,
            key="zdoom_editor",  # This key is crucial
            label_visibility="collapsed",
            help="Edit dialogue in ZDoom USDF format"
        )
    
    def render_conflict_resolution(self):
        """Render variable conflict resolution interface"""
        st.error("🚨 Variable conflicts detected!")
        st.write("The following variables have different values in plain text and USDF:")
        
        for var_key, (plain_val, usdf_val) in st.session_state.conflict_variables.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.text_input(f"Plain Text value for {var_key}", value=plain_val, disabled=True)
            
            with col2:
                st.text_input(f"USDF value for {var_key}", value=usdf_val, disabled=True)
            
            with col3:
                choice = st.radio(
                    f"Use value from:",
                    ["Plain Text", "USDF"],
                    key=f"resolve_{var_key}",
                    horizontal=True
                )
                
                if choice == "Plain Text":
                    st.session_state.master_variables[var_key] = plain_val
                else:
                    st.session_state.master_variables[var_key] = usdf_val
        
        if st.button("✅ Apply Resolution", type="secondary"):
            st.session_state.conflict_variables = {}
            st.rerun()

    def update_from_pages(self, pages: List[DialoguePage]):
        """Update all application state from parsed pages"""
        # Extract variables from the new pages
        script_variables = VariableManager.extract_variables_from_pages(pages)
        
        # Check for conflicts
        self.check_variable_conflicts(script_variables)
        
        # Merge variables
        st.session_state.master_variables = VariableManager.merge_variables(
            script_variables, 
            st.session_state.master_variables
        )
        
        # Generate both text representations from the canonical pages
        plain_text_result = DialogueParser.pages_to_plain_text(pages)
        zdoom_text_result = USDFConverter.pages_to_zdoom_text(
            pages, 
            st.session_state.actor_name,
            st.session_state.literal_output,
            st.session_state.master_variables
        )
        # Debug output
        st.info(f"Generated {len(plain_text_result)} chars of plain text and {len(zdoom_text_result)} chars of ZDoom text")

        # Update BOTH the session state AND the editor keys directly
        st.session_state.plain_text = plain_text_result
        st.session_state.zdoom_text = zdoom_text_result
        st.session_state.plain_editor = plain_text_result  # Update the widget directly
        st.session_state.zdoom_editor = zdoom_text_result  # Update the widget directly
        
        # Generate graph visualization
        st.session_state.graphviz_source = GraphvizGenerator.generate_graphviz_source(pages)
        
        # Refresh editor key to force UI update
        st.session_state.editor_key = str(uuid.uuid4())
        

    def check_variable_conflicts(self, script_variables: Dict[str, str]):
        """Check for variable value conflicts between script and master variables"""
        conflicts = {}
        
        for var_key, script_value in script_variables.items():
            if var_key in st.session_state.master_variables:
                master_value = st.session_state.master_variables[var_key]
                if script_value != master_value:
                    conflicts[var_key] = (script_value, master_value)
        
        st.session_state.conflict_variables = conflicts

    def render_variable_manager(self):
        """Render the unified variable management section"""
        st.subheader("🔤 Variable Manager")
        st.caption("Variables found in your dialogue. New or modified variables appear below.")
        
        if st.session_state.zdoom_text:
            # Get current pages for variable extraction - try both parsers safely
            try:
                # Try parsing from plain text first
                pages = DialogueParser.parse_plain_text(st.session_state.plain_text)
            except:
                try:
                    # If that fails, try parsing from ZDoom
                    pages = USDFConverter.parse_zdoom_dialogue(st.session_state.zdoom_text)
                except Exception as e:
                    st.error(f"Could not parse dialogue: {e}")
                    pages = []
            
            # Generate snippet
            snippet = VariableManager.generate_language_snippet(
                pages, 
                st.session_state.master_variables
            )
            
            if snippet:
                st.text_area(
                    "Language File Snippet (New/Changed Variables)",
                    value=snippet,
                    height=200,
                    help="Variables that are new or have different values from your language file"
                )
                
                # Download button
                st.download_button(
                    label="📥 Download Language Snippet",
                    data=snippet,
                    file_name="dialogue_snippet.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("🎉 No new or modified variables detected. All variables match your language file.")
                
        else:
            st.info("👆 Sync editors to see variables")
        
        st.markdown("---")

    def render_footer(self):
        """Render the application footer with license and attribution"""
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            **License**: GPL v3.0  
            This software is free to use, modify, and distribute under the terms of the GNU General Public License v3.0.
            """)
            
        with col2:
            st.markdown("""
            **Generated with**  
            <img src="https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/dark/deepseek-color.png" width="100">
            """, unsafe_allow_html=True)

    def run(self):
        """Main application runner"""
        self.render_header()
        self.render_sidebar()
        self.render_graph_preview()
        self.render_editors()
        self.render_variable_manager()
        self.render_footer()

# Application entry point
def main():
    app = DialogueEditorApp()
    app.run()

if __name__ == "__main__":
    main()