
from spUtils import *
import json

class spJsonWriter():

    def getColorString( self, colorDict ):
        r = hex( int( colorDict["r"] * 255 ) ).split( 'x' )[1]
        g = hex( int( colorDict["g"] * 255 ) ).split( 'x' )[1]
        b = hex( int( colorDict["b"] * 255 ) ).split( 'x' )[1]
        a = hex( int( colorDict["a"] * 255 ) ).split( 'x' )[1]
        if ( len( r ) == 1 ):
            r = '0' + r
        if ( len( g ) == 1 ):
            g = '0' + g
        if ( len( b ) == 1 ):
            b = '0' + b
        if ( len( a ) == 1 ):
            a = '0' + a
        color = r + g + b + a
        return color

    def writeAnimation( self, animation, skeletonData, jsonData ):

        jsonAnimation = { animation["name"]: {} }

        # Slot timelines
        slotIndexes = list()
        if ( len( animation["slots"] ) > 0 ):
            
            jsonAnimation[ animation["name"] ].update( { "slots": {} } )
            
            for i in range( 0, len( animation["slots"] ) ):

                slotName = skeletonData["slots"][ animation["slots"][i]["slotIndex"] ]["name"]
                slot = { slotName: {} }

                for j in range( 0, len( animation["slots"][i]["timelines"] ) ):

                    timeline = animation["slots"][i]["timelines"][j]
                    timelineTypeString = ""

                    if ( timeline["type"] == SP_TIMELINE_COLOR ):
                        timelineTypeString = "color"
                        
                        # WORKAROUND for keys with same name
                        if ( "color" in slot[slotName] ):
                            timelineTypeString = timelineTypeString + "_another_key_with_the_same_name_" + str( j )
                            
                        slot[slotName].update( { timelineTypeString: list() } )

                        for frameIndex in range( 0, len( timeline["frames"] ) ):
                            
                            frame = {}

                            frame["time"] = timeline["frames"][frameIndex]["time"]

                            frame["color"] = self.getColorString( timeline["frames"][frameIndex] )

                            curveType = timeline["frames"][frameIndex]["curve_type"]
                            curves = timeline["frames"][frameIndex]["curves"]
                            if ( curveType == SP_CURVE_STEPPED ):
                                frame["curve"] = "stepped"
                            elif ( curveType == SP_CURVE_BEZIER ):
                                frame["curve"] = curves

                            slot[slotName][timelineTypeString].append( frame )

                    elif ( timeline["type"] == SP_TIMELINE_ATTACHMENT ):
                        
                        timelineTypeString = "attachment"
                        slot[slotName].update( { timelineTypeString: list() } )

                        for frameIndex in range( 0, len( timeline["frames"] ) ):
                            
                            frame = {}

                            frame["time"] = timeline["frames"][frameIndex]["time"]
                            frame["name"] = timeline["frames"][frameIndex]["attachment_name"]

                            slot[slotName][timelineTypeString].append( frame )

                jsonAnimation[ animation["name"] ]["slots"].update( slot )


        # Bones timelines
        if ( len( animation["bones"] ) > 0 ):
            
            jsonAnimation[ animation["name"] ].update( { "bones": {} } )
            
            for i in range( 0, len( animation["bones"] ) ):

                boneName = skeletonData["bones"][ animation["bones"][i]["boneIndex"] ]["name"]
                bone = { boneName: {} }

                for j in range( 0, len( animation["bones"][i]["timelines"] ) ):
                    
                    timeline = animation["bones"][i]["timelines"][j]
                    timelineTypeString = ""

                    if ( timeline["type"] == SP_TIMELINE_ROTATE ):
                        timelineTypeString = "rotate"
                        bone[boneName].update( { timelineTypeString: list() } )

                        for frameIndex in range( 0, len( timeline["frames"] ) ):
                            
                            frame = {}

                            frame["time"] = timeline["frames"][frameIndex]["time"]

                            # SKELETON VIEWER DOESN'T ASSUME THAT OMITTED VALUES == 0
                            # Skeleton Viewer shows that angle can't be omitted
                            frame["angle"] = timeline["frames"][frameIndex]["angle"]
                                    
                            curveType = timeline["frames"][frameIndex]["curve_type"]
                            curves = timeline["frames"][frameIndex]["curves"]
                            if ( curveType == SP_CURVE_STEPPED ):
                                frame["curve"] = "stepped"
                            elif ( curveType == SP_CURVE_BEZIER ):
                                frame["curve"] = curves

                            bone[boneName][timelineTypeString].append( frame )

                    elif ( ( timeline["type"] == SP_TIMELINE_TRANSLATE ) or ( timeline["type"] == SP_TIMELINE_SCALE ) ):
                        
                        if ( timeline["type"] == SP_TIMELINE_SCALE ):
                            timelineTypeString = "scale"
                        else:
                            timelineTypeString = "translate"

                        bone[boneName].update( { timelineTypeString: list() } )

                        for frameIndex in range( 0, len( timeline["frames"] ) ):
                            
                            frame = {}
                                
                            frame["time"] = timeline["frames"][frameIndex]["time"]
                            frame["x"] = timeline["frames"][frameIndex]["x"]
                            frame["y"] = timeline["frames"][frameIndex]["y"]

                            # judging by Skeleton Viewer - can be omitted, but exported examples show them in place
##                            if ( x != 0.0 ):
##                                frame["x"] = x
##                            else:
##                                if ( math.copysign( 1, x ) == -1 ):
##                                    frame["x"] = x
##                            if ( y != 0.0 ):
##                                frame["y"] = y
##                            else:
##                                if ( math.copysign( 1, y ) == -1 ):
##                                    frame["y"] = y

                            curveType = timeline["frames"][frameIndex]["curve_type"]
                            curves = timeline["frames"][frameIndex]["curves"]
                            if ( curveType == SP_CURVE_STEPPED ):
                                frame["curve"] = "stepped"
                            elif ( curveType == SP_CURVE_BEZIER ):
                                frame["curve"] = curves

                            bone[boneName][timelineTypeString].append( frame )

                    # example of 2.1.27 json with FLIPX timeline
                    # http://esotericsoftware.com/forum/Imported-JSON-file-missing-flip-properties-3789

                    elif ( ( timeline["type"] == SP_TIMELINE_FLIPX ) or ( timeline["type"] == SP_TIMELINE_FLIPY ) ):

                        timelineTypeString = "flipX"
                        if ( timeline["type"] == SP_TIMELINE_FLIPY ):
                            timelineTypeString = "flipY"
                            
                        bone[boneName].update( { timelineTypeString: list() } )

                        for frameIndex in range( 0, len( timeline["frames"] ) ):
                            
                            frame = {}
                            frame["time"] = timeline["frames"][frameIndex]["time"]

                            if ( timeline["type"] == SP_TIMELINE_FLIPX ):
                                if ( timeline["frames"][frameIndex]["flip"] ):
                                    frame["x"] = timeline["frames"][frameIndex]["flip"]
                            else:
                                if ( timeline["frames"][frameIndex]["flip"] ):
                                    frame["y"] = timeline["frames"][frameIndex]["flip"]

                            bone[boneName][timelineTypeString].append( frame )

                jsonAnimation[ animation["name"] ]["bones"].update( bone )


        if ( len( animation["ik"] ) > 0 ):

            jsonAnimation[ animation["name"] ].update( { "ik": {} } )

            for i in range( 0, len( animation["ik"] ) ):

                name = findIkConstraintNameByIndex( animation["ik"][i]["ikConstraintIndex"], skeletonData["ikConstraints"] )

                frames = list()

                for frameIndex in range( 0, len( animation["ik"][i]["frames"] ) ):

                    time = animation["ik"][i]["frames"][frameIndex]["time"]
                    mix = animation["ik"][i]["frames"][frameIndex]["mix"]
                    bendPositive = animation["ik"][i]["frames"][frameIndex]["bendPositive"]
                    frame = { "time": time }

                    # Skeleton Viewer shows that mix can't be omitted
                    frame["mix"] = mix

                    # Skeleton Viewer shows that bendPositive can't be omitted
                    if ( bendPositive == 1 ):
                        frame["bendPositive"] = True
                    else:
                        frame["bendPositive"] = False

                    curveType = animation["ik"][i]["frames"][frameIndex]["curve_type"]
                    curves = animation["ik"][i]["frames"][frameIndex]["curves"]
                    if ( curveType == SP_CURVE_STEPPED ):
                        frame["curve"] = "stepped"
                    elif ( curveType == SP_CURVE_BEZIER ):
                        frame["curve"] = curves

                    frames.append( frame )

                jsonAnimation[ animation["name"] ]["ik"].update( { name: frames } )


        # FFD (Skin Deform) timelines
        if ( len( animation["ffd"] ) > 0 ):
            
            jsonAnimation[ animation["name"] ].update( { "ffd": {} } )
            
            for i in range( 0, len( animation["ffd"] ) ):
                
                skinName = getSkinNameByIndex( animation["ffd"][i]["skinIndex"], skeletonData["skins"] )
                jsonAnimation[ animation["name"] ]["ffd"].update( { skinName: {} } )

                for j in range( 0, len( animation["ffd"][i]["slots"] ) ):
                    
                    slotName = findSlotNameByIndex( animation["ffd"][i]["slots"][j]["slotIndex"], skeletonData["slots"] )
                    jsonAnimation[ animation["name"] ]["ffd"][skinName].update( { slotName: {} } )

                    slotDict = jsonAnimation[ animation["name"] ]["ffd"][skinName][slotName]

                    for k in range( 0, len( animation["ffd"][i]["slots"][j]["timelines"] ) ):

                        timeline = animation["ffd"][i]["slots"][j]["timelines"][k]
                        slotDict.update( { timeline["attachmentName"]: list() } )

                        for frameIndex in range( 0, len( timeline["frames"] ) ):

                            frame = { "time": 0.0 }
                            
                            frame["time"] = timeline["frames"][frameIndex]["time"]
                            
                            if ( timeline["frames"][frameIndex]["start"] != 0 ):
                                frame["offset"] = timeline["frames"][frameIndex]["start"]

                            if ( len( timeline["frames"][frameIndex]["frameVertices"] ) > 0 ):
                                frame["vertices"] = list()
                                for m in range( 0, len( timeline["frames"][frameIndex]["frameVertices"] ) ):
                                    frame["vertices"].append( timeline["frames"][frameIndex]["frameVertices"][m] )

                            curveType = timeline["frames"][frameIndex]["curve_type"]
                            curves = timeline["frames"][frameIndex]["curves"]
                            if ( curveType == SP_CURVE_STEPPED ):
                                frame["curve"] = "stepped"
                            elif ( curveType == SP_CURVE_BEZIER ):
                                frame["curve"] = curves

                            slotDict[timeline["attachmentName"]].append( frame )


        # Draw Order timelines
        if ( len( animation["drawOrder"] ) > 0 ):

            jsonAnimation[ animation["name"] ].update( { "drawOrder": list() } )

            for frameIndex in range( 0, len( animation["drawOrder"] ) ):

                frameDict = { "time": animation["drawOrder"][frameIndex]["time"] }

                offsets = animation["drawOrder"][frameIndex]["offsets"]

                if ( len( offsets ) > 0 ):
                    frameDict.update( { "offsets": list() } )

                for i in range( 0, len( offsets ) ):

                    slotName = findSlotNameByIndex( offsets[i]["slotIndex"], skeletonData["slots"] )
                    offset = { "slot": slotName, "offset": offsets[i]["amount"] }
                    frameDict["offsets"].append( offset )

                jsonAnimation[ animation["name"] ]["drawOrder"].append( frameDict )

 
        # Event timeline
        if ( len( animation["events"] ) > 0 ):
            
            jsonAnimation[ animation["name"] ].update( { "events": list() } )

            for frameIndex in range( 0, len( animation["events"] ) ):

                frame = dict()
                
                event = animation["events"][frameIndex]
                name = skeletonData["events"][ event["event"]["eventIndex"] ]["name"]

                frame.update( { "time": event["time"] } )
                frame.update( { "name": name } )

                if ( event["event"]["intValue"] != skeletonData["events"][ event["event"]["eventIndex"] ]["intValue"] ):
                    frame.update( { "int": event["event"]["intValue"] } )

                if ( event["event"]["floatValue"] != skeletonData["events"][ event["event"]["eventIndex"] ]["floatValue"] ):
                    frame.update( { "float": event["event"]["floatValue"] } )

                if ( event["event"]["stringValue"] != skeletonData["events"][ event["event"]["eventIndex"] ]["stringValue"] ):
                    frame.update( { "string": event["event"]["stringValue"] } )

                jsonAnimation[ animation["name"] ]["events"].append( frame )

        jsonData["animations"].update( jsonAnimation )


    def writeAttachment( self, attachment ):

        placeholderName = attachment["placeholderName"]
        attachmentName = attachment["attachmentName"]

        jsonAttachment = { placeholderName: {} }

        if ( attachmentName != None ):
            jsonAttachment[placeholderName]["name"] = attachmentName

        if ( attachment["attachmentType"] != SP_ATTACHMENT_REGION ):
            jsonAttachment[placeholderName]["type"] = getAttachmentTypeFromBinaryToJson( attachment["attachmentType"] )

        if ( attachment["attachmentType"] == SP_ATTACHMENT_REGION ):

            path = attachment["path"]
            if ( path != None ):
                jsonAttachment[placeholderName]["path"] = path

            x = attachment["x"]
            y = attachment["y"]
            scaleX = attachment["scaleX"]
            scaleY = attachment["scaleY"]
            rotation = attachment["rotation"]
            width = attachment["width"]
            height = attachment["height"]
            color = self.getColorString( attachment )

            if ( x != 0.0 ):
                jsonAttachment[placeholderName]["x"] = x
            else:
                if ( math.copysign( 1, x ) == -1 ):
                    jsonAttachment[placeholderName]["x"] = x
                
            if ( y != 0.0 ):
                jsonAttachment[placeholderName]["y"] = y
            else:
                if ( math.copysign( 1, y ) == -1 ):
                    jsonAttachment[placeholderName]["y"] = y
                
            if ( scaleX != 1.0 ):
                jsonAttachment[placeholderName]["scaleX"] = scaleX
            if ( scaleY != 1.0 ):
                jsonAttachment[placeholderName]["scaleY"] = scaleY
                
            if ( rotation != 0.0 ):
                jsonAttachment[placeholderName]["rotation"] = rotation
            else:
                if ( math.copysign( 1, rotation ) == -1 ):
                    jsonAttachment[placeholderName]["rotation"] = rotation
                
            jsonAttachment[placeholderName]["width"] = width
            jsonAttachment[placeholderName]["height"] = height
            if ( color != "ffffffff" ):
                jsonAttachment[placeholderName]["color"] = color

        elif ( attachment["attachmentType"] == SP_ATTACHMENT_BOUNDING_BOX ):

            jsonAttachment[placeholderName]["vertexCount"] = len( attachment["vertices"] )
            jsonAttachment[placeholderName]["vertices"] = flattenVertexList( attachment["vertices"] )

        elif ( attachment["attachmentType"] == SP_ATTACHMENT_MESH ):

            path = attachment["path"]
            if ( path != None ):
                jsonAttachment[placeholderName]["path"] = path

            mesh = attachment

            jsonAttachment[placeholderName]["uvs"] = flattenVertexList( mesh["regionUVs"] )
            jsonAttachment[placeholderName]["triangles"] = mesh["triangles"]
            jsonAttachment[placeholderName]["vertices"] = flattenVertexList( mesh["vertices"] )
            jsonAttachment[placeholderName]["hull"] = mesh["hullLength"]
            color = self.getColorString( mesh )
            if ( color != "ffffffff" ):
                jsonAttachment[placeholderName]["color"] = color

        elif ( attachment["attachmentType"] == SP_ATTACHMENT_SKINNED_MESH ):

            path = attachment["path"]
            if ( path != None ):
                jsonAttachment[placeholderName]["path"] = path

            mesh = attachment

            jsonAttachment[placeholderName]["uvs"] = flattenVertexList( mesh["regionUVs"] )
            jsonAttachment[placeholderName]["triangles"] = mesh["triangles"]
            jsonAttachment[placeholderName]["vertices"] = flattenWeightedVertexList( mesh["vertices"] )
            
            jsonAttachment[placeholderName]["hull"] = mesh["hullLength"]

            if ( len( mesh["edges"] ) > 0 ):
                jsonAttachment[placeholderName]["edges"] = mesh["edges"]

            if ( mesh["width"] > 0 ):
                jsonAttachment[placeholderName]["width"] = mesh["width"]

            if ( mesh["height"] > 0 ):
                jsonAttachment[placeholderName]["height"] = mesh["height"]
            
            color = self.getColorString( mesh )
            if ( color != "ffffffff" ):
                jsonAttachment[placeholderName]["color"] = color

        return jsonAttachment


    def writeSkin( self, skin, slots ):

        jsonSkin = { skin["name"]: {} }

        for i in range( 0, len( skin["slots"] ) ):

            slotName = findSlotNameByIndex( skin["slots"][i]["slotIndex"], slots )
            jsonSkin[ skin["name"] ][ slotName ] = {}

            for j in range( 0, len( skin["slots"][i]["attachments"] ) ):

                attachment = self.writeAttachment( skin["slots"][i]["attachments"][j] )
                jsonSkin[ skin["name"] ][ slotName ].update( attachment )

        return jsonSkin


    def writeSkeletonDataFile( self, skeletonData, path, pretty=False, blendProperty=False ):

        jsonData = { "skeleton": {} }

        jsonData["skeleton"]["hash"] = skeletonData["hash"]
        jsonData["skeleton"]["spine"] = skeletonData["version"]
        jsonData["skeleton"]["width"] = skeletonData["width"]
        jsonData["skeleton"]["height"] = skeletonData["height"]

        if ( skeletonData["nonessential"] ):
            jsonData["skeleton"]["images"] = skeletonData["images"]
            

        # Bones
        jsonData["bones"] = list()

        for i in range( 0, len( skeletonData["bones"] ) ):

            boneData = {}

            boneData["name"] = skeletonData["bones"][i]["name"]

            if ( skeletonData["bones"][i]["parent"] != -1 ):
                parentBoneIndex = skeletonData["bones"][i]["parent"]
                boneData["parent"] = jsonData["bones"][parentBoneIndex]["name"]

            if ( skeletonData["bones"][i]["length"] != 0.0 ):
                boneData["length"] = skeletonData["bones"][i]["length"]
            else:
                if ( math.copysign( 1, skeletonData["bones"][i]["length"] ) == -1 ):
                   boneData["length"] = skeletonData["bones"][i]["length"]

            if ( skeletonData["bones"][i]["x"] != 0.0 ):
                boneData["x"] = skeletonData["bones"][i]["x"]
            else:
                if ( math.copysign( 1, skeletonData["bones"][i]["x"] ) == -1 ):
                    boneData["x"] = skeletonData["bones"][i]["x"]
                
            if ( skeletonData["bones"][i]["y"] != 0.0 ):
                boneData["y"] = skeletonData["bones"][i]["y"]
            else:
                if ( math.copysign( 1, skeletonData["bones"][i]["y"] ) == -1 ):
                    boneData["y"] = skeletonData["bones"][i]["y"]

            if ( skeletonData["bones"][i]["scaleX"] != 1.0 ):
                boneData["scaleX"] = skeletonData["bones"][i]["scaleX"]
            
            if ( skeletonData["bones"][i]["scaleY"] != 1.0 ):
                boneData["scaleY"] = skeletonData["bones"][i]["scaleY"]
            
            # THERE CAN BE -0 ROTATION! and it EQUALS 0, but that's wrong!
            if ( skeletonData["bones"][i]["rotation"] != 0.0 ):
                boneData["rotation"] = skeletonData["bones"][i]["rotation"]
            else:
                if ( math.copysign( 1, skeletonData["bones"][i]["rotation"] ) == -1 ):
                    boneData["rotation"] = skeletonData["bones"][i]["rotation"]

            if ( skeletonData["bones"][i]["flipX"] ):
                boneData["flipX"] = True
                
            if ( skeletonData["bones"][i]["flipY"] ):
                boneData["flipY"] = True

            if ( not skeletonData["bones"][i]["inheritScale"] ):
                boneData["inheritScale"] = False

            if ( not skeletonData["bones"][i]["inheritRotation"] ):
                boneData["inheritRotation"] = False

            color = self.getColorString( skeletonData["bones"][i] )
            if ( color != "989898ff" ):
                boneData["color"] = color

            jsonData["bones"].append( boneData )


        # ik
        ikList = list()
        
        for i in range( 0, len( skeletonData["ikConstraints"] ) ):
            
            ik = {}
            ik["name"] = skeletonData["ikConstraints"][i]["name"]
            ik["bones"] = list()
            
            for n in range( 0, len( skeletonData["ikConstraints"][i]["bones"] ) ):
                bone = skeletonData["bones"][ skeletonData["ikConstraints"][i]["bones"][n] ]
                ik["bones"].append( bone["name"] )

            bone = skeletonData["bones"][ skeletonData["ikConstraints"][i]["target"] ]
            ik["target"] = bone["name"]
            
            mix = skeletonData["ikConstraints"][i]["mix"]
            if ( mix != 1.0 ):
                ik["mix"] = skeletonData["ikConstraints"][i]["mix"]

            if ( skeletonData["ikConstraints"][i]["bendDirection"] != 1 ):
                ik["bendPositive"] = False
            ikList.append( ik )

        if ( len( ikList ) > 0 ):
            jsonData["ik"] = ikList

        # Slots
        if ( len( skeletonData["slots"] ) > 0 ):
            
            jsonData["slots"] = list()

            for i in range( 0, len( skeletonData["slots"] ) ):
                
                slot = {}
                slot["name"] = skeletonData["slots"][i]["name"]
                slot["bone"] = skeletonData["bones"][ skeletonData["slots"][i]["boneData"] ]["name"]

                if ( skeletonData["slots"][i]["attachmentName"] ):
                    slot["attachment"] = skeletonData["slots"][i]["attachmentName"]

                color = self.getColorString( skeletonData["slots"][i] )
                if ( color != "ffffffff" ):
                    slot["color"] = color

                if ( skeletonData["slots"][i]["additiveBlending"] ):
                    if ( blendProperty ):
                        slot["blend"] = "additive"
                    else:
                        slot["additive"] = True
                
                jsonData["slots"].append( slot )
        
        # Default skin
        jsonData["skins"] = {}
        
        for i in range( 0, len( skeletonData["skins"] ) ):
            
            skin = self.writeSkin( skeletonData["skins"][i], skeletonData["slots"] )
            jsonData["skins"].update( skin )

        # Events
        if ( len( skeletonData["events"] ) > 0 ):
            
            jsonData["events"] = dict()
            
            for i in range( 0, len( skeletonData["events"] ) ):
                
                event = { skeletonData["events"][i]["name"]: dict() }
                if ( skeletonData["events"][i]["floatValue"] != 0.0 ):
                    event[ skeletonData["events"][i]["name"] ]["float"] = skeletonData["events"][i]["floatValue"]
                if ( skeletonData["events"][i]["intValue"] != 0 ):
                    event[ skeletonData["events"][i]["name"] ]["int"] = skeletonData["events"][i]["intValue"]
                if ( skeletonData["events"][i]["stringValue"] != None ):
                    event[ skeletonData["events"][i]["name"] ]["string"] = skeletonData["events"][i]["stringValue"]
                jsonData["events"].update( event )

        # Animations
        jsonData["animations"] = {}
        
        for i in range( 0, len( skeletonData["animations"] ) ):
            self.writeAnimation( skeletonData["animations"][i], skeletonData, jsonData )

        cleanupUselessFloats( jsonData )

        if ( pretty ):
            text = json.dumps( jsonData, sort_keys=False, indent=2, separators=( ",", ": " ) )
        else:
            text = json.dumps( jsonData, sort_keys=False )

        # remove "_another_key_with_the_same_name_#" from keys
        for i in range( 0, 20 ):
            text = text.replace( "_another_key_with_the_same_name_" + str( i ), "" )
        
        file = open( path, 'w' )
        file.write( text )
        file.close()
