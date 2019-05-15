
from spUtils import *
import struct

class spBinaryReader():

    def __init__( self ):
        self.m_index = 0
        self.m_byteArray = None

    def readFile( self, path ):
        file = open( path, "rb" )
        if ( not file ):
            return False
        self.m_byteArray = bytearray( file.read() )
        file.close()
        return True

    def readByte( self ):
        b = self.m_byteArray[self.m_index]
        self.m_index += 1
        return b

    def readChar( self ):
        return chr( self.readByte() )

    def readBoolean( self ):
        value = self.readByte() != 0
        return value

    def readInt( self ):
        ch1 = self.readByte()
        ch2 = self.readByte()
        ch3 = self.readByte()
        ch4 = self.readByte()
        [integer] = struct.unpack( '>i', bytes( [ch1, ch2, ch3, ch4] ) ) # big-order and signed int
        return integer

    def readShort( self ):
        ch1 = self.readByte()
        ch2 = self.readByte()
        [value] = struct.unpack(">h", bytes( [ch1, ch2] ) ) # big-order and short
        return value

    def readShorts( self ):
        count = self.readVarInt()
        arr = list()
        for i in range( 0, count ):
            arr.append( self.readShort() )
        return arr

    def readFloat( self ):
        ch1 = self.readByte()
        ch2 = self.readByte()
        ch3 = self.readByte()
        ch4 = self.readByte()
        [floating_number] = struct.unpack( '>f', bytes( [ch1, ch2, ch3, ch4] ) ) # big-order and float
        return floating_number

    def readFloats( self ):
        count = self.readVarInt()
        arr = list()
        for i in range( 0, count ):
            arr.append( self.readFloat() )
        return arr

    def readVarInt( self ):
        b = self.readByte()
        result = b & 0x7F
        if ( ( b & 0x80 ) != 0 ):
            b = self.readByte()
            result = result | ( ( b & 0x7F ) << 7 )
            if ( ( b & 0x80 ) != 0 ):
                b = self.readByte()
                result = result | ( ( b & 0x7F ) << 14 )
                if ( ( b & 0x80 ) != 0 ):
                    b = self.readByte()
                    result = result | ( ( b & 0x7F ) << 21 )
                    if ( ( b & 0x80 ) != 0 ):
                        b = self.readByte()
                        result = result | ( ( b & 0x7F ) << 28 )
        return  result

    def readString( self ):
        length = self.readVarInt()
        if ( length == 0 ):
            return None
        text = ""
        for i in range( 0, length - 1 ):
            text = text + self.readChar()
        return text

    def readColor( self, dictWithColor ):
        dictWithColor["r"] = self.readByte() / 255.0
        dictWithColor["g"] = self.readByte() / 255.0
        dictWithColor["b"] = self.readByte() / 255.0
        dictWithColor["a"] = self.readByte() / 255.0

    def readCurve( self, frame ):
        frame["curve_type"] = self.readByte()
        if ( frame["curve_type"] == SP_CURVE_BEZIER ):
            frame["curves"].append( self.readFloat() )
            frame["curves"].append( self.readFloat() )
            frame["curves"].append( self.readFloat() )
            frame["curves"].append( self.readFloat() )


    def readAnimation( self, skeletonData, name ):

        animation = { "name": name, "slots": list(), "bones": list(), "ik": list(),
                      "ffd": list(), "drawOrder": list(), "events": list() }

        # Slot timelines
        slotCount = self.readVarInt()
        #print( "animation: slotCount: " + str( slotCount ) )
        
        for i in range( 0, slotCount ):
            
            slotIndex = self.readVarInt()
            timelineCount = self.readVarInt()
            slotDict = { "slotIndex": slotIndex, "timelines": list() }

            for j in range( 0, timelineCount ):
                
                timelineType = self.readByte()
                framesCount = self.readVarInt()

                timelineDict = { "type": timelineType, "frames": list() }

                if ( timelineType == SP_TIMELINE_COLOR ):

                    for frameIndex in range( 0, framesCount ):

                        time = self.readFloat()

                        frame = { "time": time, "r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0,
                                  "curve_type": SP_CURVE_LINEAR, "curves": list() }

                        self.readColor( frame )
                        
                        if ( frameIndex < ( framesCount - 1 ) ):
                            self.readCurve( frame )

                        timelineDict["frames"].append( frame )

                elif ( timelineType == SP_TIMELINE_ATTACHMENT ):
                    
                    for frameIndex in range( 0, framesCount ):
                        
                        time = self.readFloat()
                        attachmentName = self.readString()
                        
                        frame = { "time": time, "attachment_name": attachmentName }

                        timelineDict["frames"].append( frame )

                else:
                    print( "UNKNOWN TIMELINE!" )

                slotDict["timelines"].append( timelineDict )
                        
            animation["slots"].append( slotDict )


        # Bone timelines
        boneCount = self.readVarInt()
        #print( "animation: boneCount: " + str( boneCount ) )

        for i in range( 0, boneCount ):
            
            boneIndex = self.readVarInt()
            timelineCount = self.readVarInt()
            boneDict = { "boneIndex": boneIndex, "timelines": list() }
            
            for j in range( 0, timelineCount ):
                
                timelineType = self.readByte()
                framesCount = self.readVarInt()

                timelineDict = { "type": timelineType, "frames": list() }

                if ( timelineType == SP_TIMELINE_ROTATE ):

                    for frameIndex in range( 0, framesCount ):
                        
                        time = self.readFloat()
                        angle = self.readFloat()
                        frame = { "time": time, "angle": angle, "curve_type": 0, "curves": list() }
                        
                        if ( frameIndex < ( framesCount - 1 ) ):
                            self.readCurve( frame )
                            
                        timelineDict["frames"].append( frame )

                    boneDict["timelines"].append( timelineDict )

                elif ( ( timelineType == SP_TIMELINE_TRANSLATE ) or ( timelineType == SP_TIMELINE_SCALE ) ):

                    for frameIndex in range( 0, framesCount ):
                        
                        time = self.readFloat()
                        x = self.readFloat()
                        y = self.readFloat()
                        
                        frame = { "time": time, "x": x, "y": y, "curve_type": 0, "curves": list() }
                        
                        if ( frameIndex < ( framesCount - 1 ) ):
                            self.readCurve( frame )
                            
                        timelineDict["frames"].append( frame )

                    boneDict["timelines"].append( timelineDict )

                elif ( ( timelineType == SP_TIMELINE_FLIPX ) or ( timelineType == SP_TIMELINE_FLIPY ) ):

                    for frameIndex in range( 0, framesCount ):
                        
                        time = self.readFloat()
                        flip = self.readBoolean()
                        frame = { "time": time, "flip": flip }
                        timelineDict["frames"].append( frame )

                    boneDict["timelines"].append( timelineDict )
 
                else:
                    print( "unknown timelineType: " + str( timelineType ) )

            animation["bones"].append( boneDict )


        # ik timelines
        ikCount = self.readVarInt()
        #print( "animation: ikCount: " + str( ikCount ) )

        for i in range( 0, ikCount ):
            index = self.readVarInt()
            framesCount = self.readVarInt()

            timelineDict = { "ikConstraintIndex": index, "frames": list() }

            for frameIndex in range( 0, framesCount ):

                time = self.readFloat()
                mix = self.readFloat()
                
                bendPositive = self.readByte()
                if ( bendPositive != 1 ):
                    bendPositive = -1

                frame = { "time": time, "mix": mix, "bendPositive": bendPositive, "curve_type": 0, "curves": list() }

                if ( frameIndex < ( framesCount - 1 ) ):
                    self.readCurve( frame )
                    
                timelineDict["frames"].append( frame )

            animation["ik"].append( timelineDict )


        # FFD timelines # Skin Deform timelines
        ffdCount = self.readVarInt()
        #print( "animation: ffdCount: " + str( ffdCount ) )

        for i in range( 0, ffdCount ):
            
            skinIndex = self.readVarInt()
            slotCount = self.readVarInt()
            skin = skeletonData["skins"][skinIndex]
            ffdDict = { "skinIndex": skinIndex, "slots": list() }
            
            for j in range( 0, slotCount ):
                
                slotIndex = self.readVarInt()
                timelineCount = self.readVarInt()
                slotDict = { "slotIndex": slotIndex, "timelines": list() }
                
                for k in range( 0, timelineCount ):

                    attachmentName = self.readString()
                    framesCount = self.readVarInt()
                    timelineDict = { "type": SP_TIMELINE_FFD, "attachmentName": attachmentName, "frames": list() }

                    for frameIndex in range( 0, framesCount ):

                        frame = { "time": 0.0, "end": 0, "start": 0, "frameVertices": list(), "curve_type": 0, "curves": list() }

                        frame["time"] = self.readFloat()

                        end = self.readVarInt()
                        frame["end"] = end

                        if ( end != 0 ):
                            frame["start"] = self.readVarInt()

                            end += frame["start"]
                            v = frame["start"]
                            while ( v < end ):
                                frame["frameVertices"].append( self.readFloat() )
                                v += 1

                        if ( frameIndex < ( framesCount - 1 ) ):
                            self.readCurve( frame )

                        timelineDict["frames"].append( frame )

                    slotDict["timelines"].append( timelineDict )

                ffdDict["slots"].append( slotDict )

            animation["ffd"].append( ffdDict )


        # Draw order timeline
        drawOrderFrameCount = self.readVarInt()
        #print( "animation: drawOrderCount: " + str( drawOrderFrameCount ) )
            
        for frameIndex in range( 0, drawOrderFrameCount ):

            frameDict = { "time": 0.0, "offsets": list() }

            offsetCount = self.readVarInt()
                
            for i in range( 0, offsetCount ):

                slotIndex = self.readVarInt()
                amount = self.readVarInt()
                offset = { "slotIndex": slotIndex, "amount": amount }
                frameDict["offsets"].append( offset )

            frameDict["time"] = self.readFloat()

            animation["drawOrder"].append( frameDict )


        # Event timeline
        frameCount = self.readVarInt()
        #print( "animation: eventCount: " + str( frameCount ) )

        for frameIndex in range( 0, frameCount ):
            
            time = self.readFloat()
            eventIndex = self.readVarInt()
            
            event = { "eventIndex": eventIndex,
                      "intValue": 0,
                      "floatValue": 0.0,
                      "stringValue": None }
            
            event["intValue"] = self.readVarInt()
            event["floatValue"] = self.readFloat()
            boolValue = self.readBoolean()
            
            stringValue = None
            if ( boolValue ):
                stringValue = self.readString()
            else:
                stringValue = skeletonData["events"][eventIndex]["stringValue"]
            event["stringValue"] = stringValue

            frame = { "time": time, "event": event }
            animation["events"].append( frame )

        skeletonData["animations"].append( animation )


    def readAttachment( self, skin, placeholderName, nonessential ):
        
        attachmentName = self.readString()
        attachmentType = self.readByte()

        attachment = { "placeholderName": placeholderName,
                       "attachmentType": attachmentType,
                       "attachmentName": attachmentName }

        if ( attachmentType == SP_ATTACHMENT_REGION ):

            region = attachment
            
            region["path"] = self.readString()
            region["x"] = self.readFloat()
            region["y"] = self.readFloat()
            region["scaleX"] = self.readFloat()
            region["scaleY"] = self.readFloat()
            region["rotation"] = self.readFloat()
            region["width"] = self.readFloat()
            region["height"] = self.readFloat()
            self.readColor( region )

            return region

        elif ( attachmentType == SP_ATTACHMENT_BOUNDING_BOX ):

            box = attachment
            
            box["vertices"] = deflattenVertexList( self.readFloats() )

            return box

        elif ( attachmentType == SP_ATTACHMENT_MESH ):

            mesh = attachment
            
            mesh["path"] = self.readString()         
            mesh["regionUVs"] = deflattenVertexList( self.readFloats() )
            mesh["triangles"] = self.readShorts()
            mesh["vertices"] = deflattenVertexList( self.readFloats() )
            
            self.readColor( mesh )
            
            mesh["hullLength"] = self.readVarInt()

            mesh["edges"] = list()
            mesh["width"] = 0.0
            mesh["height"] = 0.0

            if ( nonessential ):
                
                edgeCount = self.readVarInt()
                for i in range( 0, edgeCount ):
                    vertexIndex = self.readVarInt()
                    mesh["edges"].append( vertexIndex )

                mesh["width"] = self.readFloat()
                mesh["height"] = self.readFloat()
                         
            return mesh

        elif ( attachmentType == SP_ATTACHMENT_SKINNED_MESH ):

            mesh = attachment

            mesh["path"] = self.readString()
            mesh["regionUVs"] = deflattenVertexList( self.readFloats() )
            mesh["triangles"] = self.readShorts()

            verticesCount = self.readVarInt()
            vertices = list()
            i = 0
            while ( i < verticesCount ):
                vert = {}
                bonesCount = int( self.readFloat() )
                vert["bones"] = list()
                i += 1
                nn = i + bonesCount * 4
                while ( i < nn ):
                    bone = {}
                    bone["boneIndex"] = int( self.readFloat() )
                    bone["x"] = self.readFloat()
                    bone["y"] = self.readFloat()
                    bone["weight"] = self.readFloat()
                    vert["bones"].append( bone )
                    i += 4
                vertices.append( vert )
            mesh["vertices"] = vertices

            self.readColor( mesh )
            
            mesh["hullLength"] = self.readVarInt()

            mesh["edges"] = list()
            mesh["width"] = 0.0
            mesh["height"] = 0.0

            if ( nonessential ):

                edgeCount = self.readVarInt()
                for i in range( 0, edgeCount ):
                    vertexIndex = self.readVarInt()
                    mesh["edges"].append( vertexIndex )

                mesh["width"] = self.readFloat()
                mesh["height"] = self.readFloat()

            return mesh

        else:
            print( "unknown attachment type : " + str( attachmentType ) )
            return None


    def readSkin( self, skinName, nonessential ):
        
        slotCount = self.readVarInt()

        skin = { "name": skinName,
                 "slots": list() }

        for i in range( 0, slotCount ):
            slotIndex = self.readVarInt()
            attachmentCount = self.readVarInt()
            skinSlot = { "slotIndex": slotIndex, "attachments": list() }

            for j in range( 0, attachmentCount ):
                placeholderName = self.readString()
                attachment = self.readAttachment( skin, placeholderName, nonessential )
                attachment["placeholderName"] = placeholderName
                skinSlot["attachments"].append( attachment )

            skin["slots"].append( skinSlot )

        return skin


    def readSkeletonData( self ):

        skeletonData = spStoredSkeletonData()

        skeletonData["hash"] = self.readString()
        skeletonData["version"] = self.readString()
        skeletonData["width"] = self.readFloat()
        skeletonData["height"] = self.readFloat()

        skeletonData["nonessential"] = self.readBoolean()
        
        if ( skeletonData["nonessential"] ):
            #print( "nonessential == True" )
            # string images: The images path, as it was in Spine. Nonessential.
            skeletonData["images"] = self.readString()
        #else:
        #    print( "nonessential == False" )


        # Bones
        size = self.readVarInt()
        #print( "bones count: " + str( size ) )
        
        for i in range( 0, size ):

            boneData = {}
            boneData["name"] = self.readString()
            boneData["parent"] = self.readVarInt() - 1
            boneData["x"] = self.readFloat()
            boneData["y"] = self.readFloat()
            boneData["scaleX"] = self.readFloat()
            boneData["scaleY"] = self.readFloat()
            boneData["rotation"] = self.readFloat()
            boneData["length"] = self.readFloat()
            boneData["flipX"] = int( self.readBoolean() )
            boneData["flipY"] = int( self.readBoolean() )
            boneData["inheritScale"] = int( self.readBoolean() )
            boneData["inheritRotation"] = int( self.readBoolean() )
            
            # default color: 0x989898FF
            boneData["r"] = 0.596078431372549
            boneData["g"] = 0.596078431372549
            boneData["b"] = 0.596078431372549
            boneData["a"] = 1.0

            if ( skeletonData["nonessential"] ):
                self.readColor( boneData )

            skeletonData["bones"].append( boneData )


        # ik
        size = self.readVarInt()
        #print( "ik count: " + str( size ) )
        
        for i in range( 0, size ):

            ik = {}
            ik["name"] = self.readString()

            ik["bones"] = list()
            boneCount = self.readVarInt()
            for n in range( 0, boneCount ):
                boneIndex = self.readVarInt()
                ik["bones"].append( boneIndex )

            targetBoneIndex = self.readVarInt()
            ik["target"] = targetBoneIndex
            ik["mix"] = self.readFloat()
            ik["bendDirection"] = self.readByte()
            if ( ik["bendDirection"] != 1 ):
                ik["bendDirection"] = -1
                
            skeletonData["ikConstraints"].append( ik )

        # Slots
        size = self.readVarInt()
        #print( "slot count: " + str( size ) )
            
        for i in range( 0, size ):

            slotData = {}
            slotData["name"] = self.readString()
            slotData["boneData"] = self.readVarInt()
            slotData["r"] = 1.0
            slotData["g"] = 1.0
            slotData["b"] = 1.0
            slotData["a"] = 1.0
            self.readColor( slotData )
            slotData["attachmentName"] = self.readString()
            slotData["additiveBlending"] = bool( self.readByte() )
            
            skeletonData["slots"].append( slotData )

        # Default skin
        defaultSkin = self.readSkin( "default", skeletonData["nonessential"] )

        if ( defaultSkin != None ):
            skeletonData["skins"].append( defaultSkin )
        
        # User skin count
        size = self.readVarInt()
        #print( "skinSize: " + str( size ) )

        # User Skins
        if ( size > 0 ):
            for i in range( 0, size ):
                name = self.readString()
                skin = self.readSkin( name, skeletonData["nonessential"] )
                skeletonData["skins"].append( skin )

        # Events
        size = self.readVarInt()
        #print( "Events size: " + str( size ) )
        
        if ( size > 0 ):
            for i in range( 0, size ):
                eventData = { "name": self.readString() }
                eventData["intValue"] = self.readVarInt()
                eventData["floatValue"] = self.readFloat()
                eventData["stringValue"] = self.readString()
                skeletonData["events"].append( eventData )

        # Animations
        size = self.readVarInt()
        #print( "animation count: " + str( size ) )
        
        for i in range( 0, size ):
            name = self.readString()
            self.readAnimation( skeletonData, name )

        #print( "length: " + str( len( self.m_byteArray ) ) )
        #print( "index:  " + str( self.m_index ) )

        return skeletonData


    def readSkeletonDataFile( self, path ):
        self.m_index = 0
        self.m_byteArray = None
        
        if ( not self.readFile( path ) ):
            return None

        skeletonData = self.readSkeletonData()
        return skeletonData
