
import math

SP_ATTACHMENT_REGION       = 0
SP_ATTACHMENT_BOUNDING_BOX = 1
SP_ATTACHMENT_MESH         = 2
SP_ATTACHMENT_SKINNED_MESH = 3

SP_TIMELINE_SCALE        = 0
SP_TIMELINE_ROTATE       = 1
SP_TIMELINE_TRANSLATE    = 2
SP_TIMELINE_ATTACHMENT   = 3
SP_TIMELINE_COLOR        = 4
SP_TIMELINE_FLIPX        = 5
SP_TIMELINE_FLIPY        = 6
SP_TIMELINE_FFD          = 7
SP_TIMELINE_IKCONSTRAINT = 8

SP_CURVE_LINEAR  = 0
SP_CURVE_STEPPED = 1
SP_CURVE_BEZIER  = 2

def deflattenVertexList( vertices ):
    deflattenedVertexList = list()
    for i in range( 0, len( vertices ), 2 ):
        deflattenedVertexList.append( { "x": vertices[i], "y": vertices[i+1] } )
        
    return deflattenedVertexList

def flattenVertexList( vertices ):
    flattenedVertexList = list()
    for i in range( 0, len( vertices ) ):
        flattenedVertexList.append( vertices[i]["x"] )
        flattenedVertexList.append( vertices[i]["y"] )
        
    return flattenedVertexList

def deflattenWeightedVertexList( vertices ):
    deflattenedVertices = list()
    i = 0
    while ( i < len( vertices ) ):
        vert = {}
        bonesCount = int( vertices[i] )
        vert["bones"] = list()
        i += 1
        nn = i + bonesCount * 4
        while ( i < nn ):
            bone = {}
            bone["boneIndex"] = int( vertices[i] )
            bone["x"] = vertices[i+1]
            bone["y"] = vertices[i+2]
            bone["weight"] = vertices[i+3]
            vert["bones"].append( bone )
            i += 4
        deflattenedVertices.append( vert )
        
    return deflattenedVertices

def flattenWeightedVertexList( vertices ):
    flattenedVertices = list()
    for i in range( 0, len( vertices ) ):
        flattenedVertices.append( float( len( vertices[i]["bones"] ) ) )
        for j in range( 0, len( vertices[i]["bones"] ) ):
            flattenedVertices.append( float( vertices[i]["bones"][j]["boneIndex"] ) )
            flattenedVertices.append( vertices[i]["bones"][j]["x"] )
            flattenedVertices.append( vertices[i]["bones"][j]["y"] )
            flattenedVertices.append( vertices[i]["bones"][j]["weight"] )

    return flattenedVertices

def getSkinNameByIndex( index, skins ):
    return skins[index]["name"]

def getSkinIndexByName( name, skins ):
    for i in range( 0, len( skins ) ):
        if ( skins[i]["name"] == name ):
            return i

def getAttachmentTypeFromJsonToBinary( value ):
    if ( value == None ):
        return SP_ATTACHMENT_REGION
    elif ( value == "boundingbox" ):
        return SP_ATTACHMENT_BOUNDING_BOX
    elif ( value == "mesh" ):
        return SP_ATTACHMENT_MESH
    elif ( value == "skinnedmesh" ):
        return SP_ATTACHMENT_SKINNED_MESH

def getAttachmentTypeFromBinaryToJson( value ):
    if ( value == SP_ATTACHMENT_REGION ):
        return None
    elif ( value == SP_ATTACHMENT_BOUNDING_BOX ):
        return "boundingbox"
    elif ( value == SP_ATTACHMENT_MESH ):
        return "mesh"
    elif ( value == SP_ATTACHMENT_SKINNED_MESH ):
        return "skinnedmesh"

def findSlotNameByIndex( index, slots ):
    return slots[index]["name"]

def findSlotIndexByName( name, slots ):
    for i in range( 0, len( slots ) ):
        if ( slots[i]["name"] == name ):
            return i

def findEventIndexByName( name, events ):
    for i in range( 0, len( events ) ):
        if ( name == events[i]["name"] ):
            return i

def findIkConstraintNameByIndex( index, iks ):
    return iks[index]["name"]

def findIkConstraintIndexByName( name, iks ):
    for i in range( 0, len( iks ) ):
        if ( name == iks[i]["name"] ):
            return i

def findBoneIndexByName( name, bonesList ):
    for i in range( 0, len( bonesList ) ):
        if ( bonesList[i]["name"] == name ):
            return i

def findBoneParentIndexByName( name, bonesList ):
    i = len( bonesList ) - 1
    while ( i > -1 ):
        if ( bonesList[i]["name"] == name ):
            return i
        i -= 1

def spStoredSkeletonData():
    skeletonData = { "hash": None,
                     "version": None,
                     "width": 0.0,
                     "height": 0.0,
                     "images": None,
                     "nonessential": False,
                     "bones": list(),
                     "ikConstraints": list(),
                     "slots": list(),
                     "skins": list(),
                     "events": list(),
                     "animations": list() }
    return skeletonData

def trimFloatValue( obj, key ):
    if ( obj[key].is_integer() ):
        if ( obj[key] == 0.0 ):
            # for some reason -0 doesn't work, so leave as -0.0
            if ( math.copysign( 1, obj[key] ) == -1 ):
                obj[key] = -0.0
            else:
                obj[key] = 0
        else:
            obj[key] = int( obj[key] )
    # spine's json export has formatted floats
    # example: 2.7799999713897705 is 2.78

##    else:
##        value = "{0:.7g}".format( obj[key] )
##        obj[key] = float( value )

def traverseList( _list ):
    for i in range( 0, len( _list ) ):
        
        if ( type( _list[i] ) is float ):
            trimFloatValue( _list, i )
        
        elif ( type( _list[i] ) is dict ):
            traverseDict( _list[i] )
            
        elif ( type( _list[i] ) is list ):
            traverseList( _list[i] )

def traverseDict( obj ):
    keyList = list( obj.keys() )
    for i in range( 0, len( keyList ) ):
        
        if ( type( obj[keyList[i]] ) is float ):
            trimFloatValue( obj, keyList[i] )
        
        elif ( type( obj[keyList[i]] ) is dict ):
            traverseDict( obj[keyList[i]] )
            
        elif ( type( obj[keyList[i]] ) is list ):
            traverseList( obj[keyList[i]] )

def cleanupUselessFloats( obj ):
    if ( type( obj ) is dict ):
        traverseDict( obj )
