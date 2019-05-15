
def readAtlasFile( path ):

    file = open( path, 'r' )
    text = file.read()
    file.close()

    lines = text.split( '\n' )

    atlas = []

    i = 0
    while ( i < len( lines ) ):
        
        if ( lines[i] == "" ):
            if ( i == len( lines ) - 1 ):
                break
            
            atlas.append( dict() )
            i += 1
            continue
            
        atlas[-1]["name"] = lines[i]
        
        splitted = lines[i+1].split( "size: " )[1].split( "," )
        atlas[-1]["width"] = int( splitted[0] )
        atlas[-1]["height"] = int( splitted[1] )

        atlas[-1]["format"] = lines[i+2].split( "format: " )[1]

        splitted = lines[i+3].split( "filter: " )[1].split( "," )
        atlas[-1]["filter"] = { "minification": splitted[0],
                                "magnification": splitted[1] }

        atlas[-1]["repeat"] = lines[i+4].split( "repeat: " )[1]

        atlas[-1]["regionSections"] = list()

        i += 5

        while ( True ):

            if ( lines[i] == "" ):
                break

            region = dict()

            region["name"] = lines[i]
            i += 1

            region["rotate"] = False
            if ( lines[i].split( "rotate: " )[1] == "true" ):
                region["rotate"] = True
            i += 1

            xy = lines[i].split( "xy: " )[1].split( ", " )
            region["x"] = int( xy[0] )
            region["y"] = int( xy[1] )
            i += 1

            size = lines[i].split( "size: " )[1].split( ", " )
            region["width"] = int( size[0] )
            region["height"] = int( size[1] )
            i += 1

            # can be ommited
            region["split"] = None
            if ( "split: " in lines[i] ):
                splits = lines[i].split( "split: " )[1].split( ", " )
                region["split"] = { "left": int( splits[0] ),
                                    "right": int( splits[1] ),
                                    "top": int( splits[2] ),
                                    "bottom": int( splits[3] ) }
                i += 1

            # can be ommited
            # WILL be ommited if "split" wasn't added
            region["pad"] = None
            if ( "pad: " in lines[i] ):
                pads = lines[i].split( "pad: " )[1].split( ", " )
                region["pad"] = { "left": int( pads[0] ),
                                  "right": int( pads[1] ),
                                  "top": int( pads[2] ),
                                  "bottom": int( pads[3] ) }
                i += 1

            orig = lines[i].split( "orig: " )[1].split( ", " )
            region["originalWidth"] = int( orig[0] )
            region["originalHeight"] = int( orig[1] )
            i += 1

            offset = lines[i].split( "offset: " )[1].split( ", " )
            region["offsetLeft"] = int( offset[0] )
            region["offsetBottom"] = int( offset[1] )
            i += 1

            region["index"] = int( lines[i].split( "index: " )[1] )
            i += 1

            atlas[-1]["regionSections"].append( region )

    return atlas


def writeAtlasFile( atlas, path ):

    atlasText = "\n"

    for i in range( 0, len( atlas ) ):
        atlasText = atlasText + atlas[i]["name"] + "\n"
        atlasText = atlasText + "size: " + str( int( atlas[i]["width"] ) ) + "," + str( int( atlas[i]["height"] ) ) + "\n"
        atlasText = atlasText + "format: " + atlas[i]["format"] + "\n"
        atlasText = atlasText + "filter: " + atlas[i]["filter"]["minification"] + "," + atlas[i]["filter"]["magnification"] + "\n"
        atlasText = atlasText + "repeat: " + atlas[i]["repeat"] + "\n"

        for j in range( 0, len( atlas[i]["regionSections"] ) ):
            region = atlas[i]["regionSections"][j]
            atlasText = atlasText + region["name"] + "\n"
            atlasText = atlasText + "  rotate: " + str( region["rotate"] ).lower() + "\n"
            atlasText = atlasText + "  xy: " + str( int( region["x"] ) ) + ", " + str( int( region["y"] ) ) + "\n"
            atlasText = atlasText + "  size: " + str( int( region["width"] ) ) + ", " + str( int( region["height"] ) ) + "\n"

            # can be ommited
            if ( region["split"] ):
                atlasText = atlasText + "  split: " + str( int( region["split"]["left"] ) ) + ", " + str( int( region["split"]["right"] ) )
                atlasText = atlasText + ", " + str( int( region["split"]["top"] ) ) + ", " + str( int( region["split"]["bottom"] ) ) + "\n"

                # can be ommited
                # WILL be ommited if "split" wasn't added
                if ( region["pad"] ):
                    atlasText = atlasText + "  pad: " + str( int( region["pad"]["left"] ) ) + ", " + str( int( region["pad"]["right"] ) )
                    atlasText = atlasText + ", " + str( int( region["pad"]["top"] ) ) + ", " + str( int( region["pad"]["bottom"] ) ) + "\n"
            
            atlasText = atlasText + "  orig: " + str( int( region["originalWidth"] ) ) + ", " + str( int( region["originalHeight"] ) ) + "\n"
            atlasText = atlasText + "  offset: " + str( int( region["offsetLeft"] ) ) + ", " + str( int( region["offsetBottom"] ) ) + "\n"
            atlasText = atlasText + "  index: " + str( int( region["index"] ) ) + "\n"

    file = open( path, 'w' )
    file.write( atlasText )
    file.close()


