void Main() {
}

void RenderMenu() {
    if (UI::BeginMenu("TMRL Tools")) {
        if (UI::MenuItem("Export track to CSV")) {
            ExportTrackCenterline();
        }
        UI::EndMenu();
    }
}

void ExportTrackCenterline() {
    auto app = GetApp();
    auto map = app.RootMap;
    
    if (map == null) {
        print("Error: Map is not loaded!");
        return;
    }

    IO::File file(IO::FromStorageFolder("track_centerline.csv"), IO::FileMode::Write);
    file.WriteLine("GridX,GridY,GridZ,Dir,BlockName");

    uint count = 0;
    
    for (uint i = 0; i < map.Blocks.Length; i++) {
        auto block = map.Blocks[i];
        if (block.BlockModel == null) continue;
        
        string name = block.BlockModel.IdName;
        
        if (name.ToLower().Contains("road")) {
            auto coord = block.Coord;
            
            int dir = block.Dir; 
            
            file.WriteLine(coord.x + "," + coord.y + "," + coord.z + "," + dir + "," + name);
            count++;
        }
    }
    
    file.Close();
    print("Success! Exported " + count + " blocks.");
}
