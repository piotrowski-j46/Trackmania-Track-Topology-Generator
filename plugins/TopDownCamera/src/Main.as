[MenuItem("Set camera to 90 degrees", "Tools")]
void Main() {
    CGameCtnApp@ app = GetApp();
    
    auto editor = cast<CGameCtnEditorFree>(app.Editor);
    if (editor is null) {
        print("Error: Track editor must be open!");
        return;
    }

    auto pmt = editor.PluginMapType;
    if (pmt is null) {
        print("Error: Failed to connect to CGameEditorPluginMap.");
        return;
    }

    pmt.CameraVAngle = Math::PI / 2.0; 
    
    pmt.CameraHAngle = 0.0;
    
    
    print("Camera set: Top-Down");
}
