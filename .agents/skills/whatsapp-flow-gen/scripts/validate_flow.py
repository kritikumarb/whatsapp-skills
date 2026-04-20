import json
import sys

def validate_flow(flow_path):
    with open(flow_path, 'r') as f:
        flow = json.load(f)
    
    errors = []
    
    # Top-level checks
    if flow.get("version") != "7.1":
        errors.append("ERROR: 'version' must be '7.1'")
    if flow.get("data_api_version") != "3.0":
        errors.append("ERROR: 'data_api_version' must be '3.0'")
    if "routing_model" not in flow:
        errors.append("ERROR: 'routing_model' is mandatory")
        
    # Per-screen checks
    for screen in flow.get("screens", []):
        sid = screen.get("id")
        children = screen.get("layout", {}).get("children", [])
        
        # Check component isolation for NavigationList
        has_nav_list = any(c.get("type") == "NavigationList" for c in children)
        if has_nav_list and len(children) > 1:
            errors.append(f"ERROR screen '{sid}': NavigationList must be the ONLY component (Rule X-004)")
            
        # Check exclusivity for PhotoPicker/DocumentPicker
        has_photo = any(c.get("type") == "PhotoPicker" for c in children)
        has_doc = any(c.get("type") == "DocumentPicker" for c in children)
        if has_photo and has_doc:
            errors.append(f"ERROR screen '{sid}': PhotoPicker and DocumentPicker are mutually exclusive (Rule X-003)")
            
        # Check footer symmetry in If
        for c in children:
            if c.get("type") == "If":
                then_branch = c.get("then", [])
                else_branch = c.get("else", [])
                has_footer_then = any(cc.get("type") == "Footer" for cc in then_branch)
                has_footer_else = any(cc.get("type") == "Footer" for cc in else_branch)
                if has_footer_then != has_footer_else:
                    errors.append(f"ERROR screen '{sid}': Footer inside 'If' must exist in BOTH branches (Rule X-006)")

        # Check char limits for TextHeading, TextSubheading
        for c in children:
            if c.get("type") in ["TextHeading", "TextSubheading"]:
                text = c.get("text", "")
                if len(text) > 80:
                    errors.append(f"ERROR screen '{sid}': {c.get('type')} text exceeds 80 chars (current: {len(text)}) (Rule TH-001/TS-001)")
            if c.get("type") == "TextInput":
                label = c.get("label", "")
                if len(label) > 20:
                    errors.append(f"ERROR screen '{sid}': TextInput label exceeds 20 chars (current: {len(label)}) (Rule TI-002)")
                    
    if errors:
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("Flow is valid.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_flow.py <path_to_flow.json>")
        sys.exit(1)
    validate_flow(sys.argv[1])
