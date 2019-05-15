
import struct
from spUtils import *

class spBinaryWriter():

    def __init__( self ):
        self.m_byteArray = bytearray()

    def writeByte( self, value ):
        self.m_byteArray.extend( value.to_bytes( 1, byteorder="big" ) )

    def writeBoolean( self, value ):
        self.m_byteArray.extend( int( value ).to_bytes( 1, byteorder="big" ) )

    def writeInt( self, value ):
        bval = struct.pack( '>i', value ) # big-order and signed int
        self.m_byteArray.extend( bval )

    def writeShort( self, value ):
        bval = struct.pack(">h", value ) # big-order and short
        self.writeByte( bval[0] )
        self.writeByte( bval[1] )

    def writeShorts( self, values ):
        self.writeVarInt( len( values ) )
        for i in range( 0, len( values ) ):
            self.writeShort( values[i] )

    def writeFloat( self, value ):
        value = struct.pack( '>f', value )
        self.m_byteArray.extend( value )

    def writeFloats( self, values ):
        self.writeVarInt( len( values ) )
        for i in range( 0, len( values ) ):
            self.writeFloat( values[i] )

    def writeVarInt( self, value ):
        byteArray = bytearray()
        while ( True ):
            byte = value & 0x7f
            value = value >> 7
            if ( value ):
                self.writeByte( byte | 0x80 )
            else:
                self.writeByte( byte )
                break

    def writeString( self, text ):
        if ( text == None ):
            self.writeVarInt( 0 )
        else:
            length = len( text )
            self.writeVarInt( length + 1 ) # for '\0' which .skel files don't have anyway...
            for i in range( 0, length ):
                self.writeByte( ord( text[i] ) )

    def writeColor( self, dictWithColor ):
        self.writeByte( int( dictWithColor["r"] * 255 ) )
        self.writeByte( int( dictWithColor["g"] * 255 ) )
        self.writeByte( int( dictWithColor["b"] * 255 ) )
        self.writeByte( int( dictWithColor["a"] * 255 ) )

    def writeCurve( self, frame ):
        self.writeByte( frame["curve_type"] )
        if ( frame["curve_type"] == SP_CURVE_BEZIER ):
            self.writeFloat( frame["curves"][0] )
            self.writeFloat( frame["curves"][1] )
            self.writeFloat( frame["curves"][2] )
            self.writeFloat( frame["curves"][3] )

    def writeAnimation( self, animation, skeletonData ):

        # Slot timelines
        self.writeVarInt( len( animation["slots"] ) )

        for i in range( 0, len( animation["slots"] ) ):

            self.writeVarInt( animation["slots"][i]["slotIndex"] )
            self.writeVarInt( len( animation["slots"][i]["timelines"] ) )

            for j in range( 0, len( animation["slots"][i]["timelines"] ) ):

                timeline = animation["slots"][i]["timelines"][j]
                self.writeByte( timeline["type"] )
                self.writeVarInt( len( timeline["frames"] ) )

                if ( timeline["type"] == SP_TIMELINE_COLOR ):

                    for frameIndex in range( 0, len( timeline["frames"] ) ):

                        self.writeFloat( timeline["frames"][frameIndex]["time"] )
                        self.writeColor( timeline["frames"][frameIndex] )
                        if ( frameIndex < ( len( timeline["frames"] ) - 1 ) ):
                            self.writeCurve( timeline["frames"][frameIndex] )

                elif ( timeline["type"] == SP_TIMELINE_ATTACHMENT ):

                    for frameIndex in range( 0, len( timeline["frames"] ) ):
                        
                        self.writeFloat( timeline["frames"][frameIndex]["time"] )
                        self.writeString( timeline["frames"][frameIndex]["attachment_name"] )

                else:
                    print( "UNKNOWN TIMELINE BW" )


        # Bone timelines
        self.writeVarInt( len( animation["bones"] ) )

        for i in range( 0, len( animation["bones"] ) ):
            
            self.writeVarInt( animation["bones"][i]["boneIndex"] )
            self.writeVarInt( len( animation["bones"][i]["timelines"] ) )

            for j in range( 0, len( animation["bones"][i]["timelines"] ) ):
                
                timeline = animation["bones"][i]["timelines"][j]
                self.writeByte( timeline["type"] )
                self.writeVarInt( len( timeline["frames"] ) )

                if ( timeline["type"] == SP_TIMELINE_ROTATE ):

                    for frameIndex in range( 0, len( timeline["frames"] ) ):
                        
                        self.writeFloat( timeline["frames"][frameIndex]["time"] )
                        self.writeFloat( timeline["frames"][frameIndex]["angle"] )

                        if ( frameIndex < ( len( timeline["frames"] ) - 1 ) ):
                            self.writeCurve( timeline["frames"][frameIndex] )

                elif ( ( timeline["type"] == SP_TIMELINE_TRANSLATE ) or ( timeline["type"] == SP_TIMELINE_SCALE ) ):

                    for frameIndex in range( 0, len( timeline["frames"] ) ):
                        
                        self.writeFloat( timeline["frames"][frameIndex]["time"] )
                        self.writeFloat( timeline["frames"][frameIndex]["x"] )
                        self.writeFloat( timeline["frames"][frameIndex]["y"] )

                        if ( frameIndex < ( len( timeline["frames"] ) - 1 ) ):
                            self.writeCurve( timeline["frames"][frameIndex] )

                elif ( ( timeline["type"] == SP_TIMELINE_FLIPX ) or ( timeline["type"] == SP_TIMELINE_FLIPY ) ):

                    for frameIndex in range( 0, len( timeline["frames"] ) ):
                        
                        self.writeFloat( timeline["frames"][frameIndex]["time"] )
                        self.writeBoolean( timeline["frames"][frameIndex]["flip"] )
                    
                else:
                    print( "another timeline type" )


        # ik timelines
        self.writeVarInt( len( animation["ik"] ) )

        for i in range( 0, len( animation["ik"] ) ):
            
            self.writeVarInt( animation["ik"][i]["ikConstraintIndex"] )
            self.writeVarInt( len( animation["ik"][i]["frames"] ) )

            for frameIndex in range( 0, len( animation["ik"][i]["frames"] ) ):

                frame = animation["ik"][i]["frames"][frameIndex]

                self.writeFloat( frame["time"] )
                self.writeFloat( frame["mix"] )

                if ( frame["bendPositive"] != 1 ):
                    self.writeByte( 255 )
                else:
                    self.writeByte( frame["bendPositive"] )

                if ( frameIndex < ( len( animation["ik"][i]["frames"] ) - 1 ) ):
                    self.writeCurve( frame )


        # FFD timelines
        self.writeVarInt( len( animation["ffd"] ) )

        for i in range( 0, len( animation["ffd"] ) ):
            
            self.writeVarInt( animation["ffd"][i]["skinIndex"] )
            self.writeVarInt( len( animation["ffd"][i]["slots"] ) )
            
            for j in range( 0, len( animation["ffd"][i]["slots"] ) ):
                
                self.writeVarInt( animation["ffd"][i]["slots"][j]["slotIndex"] )
                self.writeVarInt( len( animation["ffd"][i]["slots"][j]["timelines"] ) )
                
                for k in range( 0, len( animation["ffd"][i]["slots"][j]["timelines"] ) ):

                    timeline = animation["ffd"][i]["slots"][j]["timelines"][k]

                    self.writeString( timeline["attachmentName"] )
                    self.writeVarInt( len( timeline["frames"] ) )

                    for frameIndex in range( 0, len( timeline["frames"] ) ):

                        self.writeFloat( timeline["frames"][frameIndex]["time"] )
                        self.writeVarInt( timeline["frames"][frameIndex]["end"] )

                        if ( timeline["frames"][frameIndex]["end"] > 0 ):
                            self.writeVarInt( timeline["frames"][frameIndex]["start"] )

                            for m in range( 0, len( timeline["frames"][frameIndex]["frameVertices"] ) ):
                                self.writeFloat( timeline["frames"][frameIndex]["frameVertices"][m] )

                        if ( frameIndex < ( len( timeline["frames"] ) - 1 ) ):
                            self.writeCurve( timeline["frames"][frameIndex] )


        # Draw order timeline
        self.writeVarInt( len( animation["drawOrder"] ) )

        for frameIndex in range( 0, len( animation["drawOrder"] ) ):

            frame = animation["drawOrder"][frameIndex]

            self.writeVarInt( len( frame["offsets"] ) )
                
            for i in range( 0, len( frame["offsets"] ) ):

                self.writeVarInt( frame["offsets"][i]["slotIndex"] )
                self.writeVarInt( frame["offsets"][i]["amount"] )

            self.writeFloat( frame["time"] )


        # Event timeline
        self.writeVarInt( len( animation["events"] ) )
        
        for frameIndex in range( 0, len( animation["events"] ) ):
            
            event = animation["events"][frameIndex]["event"]
            self.writeFloat( animation["events"][frameIndex]["time"] )
            self.writeVarInt( event["eventIndex"] )
            self.writeVarInt( event["intValue"] )
            self.writeFloat( event["floatValue"] )
            
            boolValue = False
            if ( event["stringValue"] != skeletonData["events"][ event["eventIndex"] ]["stringValue"] ):
                boolValue = True
            self.writeBoolean( boolValue )
            
            if ( boolValue ):
                self.writeString( event["stringValue"] )


    def writeAttachment( self, attachment, nonessential ):

        placeholderName = attachment["placeholderName"]
        attachmentName = attachment["attachmentName"]

        self.writeString( attachmentName )
        self.writeByte( attachment["attachmentType"] )

        if ( attachment["attachmentType"] == SP_ATTACHMENT_REGION ):

            path = attachment["path"]

            self.writeString( path )
            
            self.writeFloat( attachment["x"] )
            self.writeFloat( attachment["y"] )
            self.writeFloat( attachment["scaleX"] )
            self.writeFloat( attachment["scaleY"] )
            self.writeFloat( attachment["rotation"] )
            self.writeFloat( attachment["width"] )
            self.writeFloat( attachment["height"] )
            self.writeColor( attachment )

        elif ( attachment["attachmentType"] == SP_ATTACHMENT_BOUNDING_BOX ):

            self.writeFloats( flattenVertexList( attachment["vertices"] ) )

        elif ( attachment["attachmentType"] == SP_ATTACHMENT_MESH ):
            
            path = attachment["path"]

            self.writeString( path )

            mesh = attachment

            self.writeFloats( flattenVertexList( mesh["regionUVs"] ) )
            self.writeShorts( mesh["triangles"] )
            self.writeFloats( flattenVertexList( mesh["vertices"] ) )
            self.writeColor( mesh )
            self.writeVarInt( mesh["hullLength"] )

            if ( nonessential ):

                self.writeVarInt( len( mesh["edges"] ) )
                for i in range( 0, len( mesh["edges"] ) ):
                    self.writeVarInt( mesh["edges"][i] )

                self.writeFloat( mesh["width"] )
                self.writeFloat( mesh["height"] )

        elif ( attachment["attachmentType"] == SP_ATTACHMENT_SKINNED_MESH ):
            
            path = attachment["path"]
            
            self.writeString( path )

            mesh = attachment

            self.writeFloats( flattenVertexList( mesh["regionUVs"] ) )
            self.writeShorts( mesh["triangles"] )

            verticesData = list()
            for i in range( 0, len( mesh["vertices"] ) ):
                verticesData.append( float( len( mesh["vertices"][i]["bones"] ) ) )
                for j in range( 0, len( mesh["vertices"][i]["bones"] ) ):
                    verticesData.append( float( mesh["vertices"][i]["bones"][j]["boneIndex"] ) )
                    verticesData.append( mesh["vertices"][i]["bones"][j]["x"] )
                    verticesData.append( mesh["vertices"][i]["bones"][j]["y"] )
                    verticesData.append( mesh["vertices"][i]["bones"][j]["weight"] )

            self.writeVarInt( len( verticesData ) )
            for i in range( 0, len( verticesData ) ):
                self.writeFloat( verticesData[i] )

            self.writeColor( mesh )
            self.writeVarInt( mesh["hullLength"] )

            if ( nonessential ):

                self.writeVarInt( len( mesh["edges"] ) )
                for i in range( 0, len( mesh["edges"] ) ):
                    self.writeVarInt( mesh["edges"][i] )

                self.writeFloat( mesh["width"] )
                self.writeFloat( mesh["height"] )


    def writeSkin( self, skin, nonessential ):
        self.writeVarInt( len( skin["slots"] ) )

        for i in range( 0, len( skin["slots"] ) ):
            
            self.writeVarInt( skin["slots"][i]["slotIndex"] )
            self.writeVarInt( len( skin["slots"][i]["attachments"] ) )

            for j in range( 0, len( skin["slots"][i]["attachments"] ) ):
                self.writeString( skin["slots"][i]["attachments"][j]["placeholderName"] )
                self.writeAttachment( skin["slots"][i]["attachments"][j], nonessential )


    def writeSkeletonDataFile( self, skeletonData, path ):

        self.m_byteArray = bytearray()

        self.writeString( skeletonData["hash"] )
        self.writeString( skeletonData["version"] )
        self.writeFloat( skeletonData["width"] )
        self.writeFloat( skeletonData["height"] )

        self.writeBoolean( skeletonData["nonessential"] )
        
        if ( skeletonData["nonessential"] ):
            # string images: The images path, as it was in Spine. Nonessential.
            #print( "binary write: nonessential == True" )
            self.writeString( skeletonData["images"] )

        # Bones
        self.writeVarInt( len( skeletonData["bones"] ) )
        
        for i in range( 0, len( skeletonData["bones"] ) ):
            
            self.writeString( skeletonData["bones"][i]["name"] )
            self.writeVarInt( skeletonData["bones"][i]["parent"] + 1 )

            self.writeFloat( skeletonData["bones"][i]["x"] )
            self.writeFloat( skeletonData["bones"][i]["y"] )
            self.writeFloat( skeletonData["bones"][i]["scaleX"] )
            self.writeFloat( skeletonData["bones"][i]["scaleY"] )
            self.writeFloat( skeletonData["bones"][i]["rotation"] )
            self.writeFloat( skeletonData["bones"][i]["length"] )
            self.writeBoolean( bool( skeletonData["bones"][i]["flipX"] ) )
            self.writeBoolean( bool( skeletonData["bones"][i]["flipY"] ) )
            self.writeBoolean( bool( skeletonData["bones"][i]["inheritScale"] ) )
            self.writeBoolean( bool( skeletonData["bones"][i]["inheritRotation"] ) )

            if ( skeletonData["nonessential"] ):
                self.writeColor( skeletonData["bones"][i] )

        # ik
        self.writeVarInt( len( skeletonData["ikConstraints"] ) )
        
        for i in range( 0, len( skeletonData["ikConstraints"] ) ):
            
            self.writeString( skeletonData["ikConstraints"][i]["name"] )
            self.writeVarInt( len( skeletonData["ikConstraints"][i]["bones"] ) )

            for n in range( 0, len( skeletonData["ikConstraints"][i]["bones"] ) ):
                self.writeVarInt( skeletonData["ikConstraints"][i]["bones"][n] )

            self.writeVarInt( skeletonData["ikConstraints"][i]["target"] )
            self.writeFloat( skeletonData["ikConstraints"][i]["mix"] )

            if ( skeletonData["ikConstraints"][i]["bendDirection"] == -1 ):
                self.writeByte( 255 )
            else:
                self.writeByte( skeletonData["ikConstraints"][i]["bendDirection"] )

        # Slots
        self.writeVarInt( len( skeletonData["slots"] ) )
        
        if ( len( skeletonData["slots"] ) > 0 ):
            
            for i in range( 0, len( skeletonData["slots"] ) ):
                
                self.writeString( skeletonData["slots"][i]["name"] )
                self.writeVarInt( skeletonData["slots"][i]["boneData"] )
                self.writeColor( skeletonData["slots"][i] )
                self.writeString( skeletonData["slots"][i]["attachmentName"] )
                self.writeByte( skeletonData["slots"][i]["additiveBlending"] )
        
        # Default skin
        self.writeSkin( skeletonData["skins"][0], skeletonData["nonessential"] )

        # User skin count
        size = len( skeletonData["skins"] ) - 1
        self.writeVarInt( size ) # default one doesn't count

        # Skins
        if ( size > 0 ):
            for i in range( i, len( skeletonData["skins"] ) ):
                self.writeString( skeletonData["skins"][i]["name"] )
                self.writeSkin( skeletonData["skins"][i], skeletonData["nonessential"] )

        # Events
        self.writeVarInt( len( skeletonData["events"] ) )
        
        if ( len( skeletonData["events"] ) > 0 ):
            
            for i in range( 0, len( skeletonData["events"] ) ):
                
                self.writeString( skeletonData["events"][i]["name"] )
                self.writeVarInt( skeletonData["events"][i]["intValue"] )
                self.writeFloat( skeletonData["events"][i]["floatValue"] )
                self.writeString( skeletonData["events"][i]["stringValue"] )

        # Animations
        self.writeVarInt( len( skeletonData["animations"] ) )
        
        for i in range( 0, len( skeletonData["animations"] ) ):

            self.writeString( skeletonData["animations"][i]["name"] )
            self.writeAnimation( skeletonData["animations"][i], skeletonData )
        
        file = open( path, 'wb' )
        file.write( self.m_byteArray )
        file.close()
