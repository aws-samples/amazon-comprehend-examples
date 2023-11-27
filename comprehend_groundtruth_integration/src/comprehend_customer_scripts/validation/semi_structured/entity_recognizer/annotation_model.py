import enum
from marshmallow import EXCLUDE, Schema, fields, validates_schema, ValidationError, validate


class Fields(enum.Enum):
    VERSION = 'Version'
    DOCUMENT_TYPE = 'DocumentType'
    DOCUMENT_METADATA = 'DocumentMetadata'
    BLOCKS = 'Blocks'
    ENTITIES = 'Entities'


# Entities objects


class EntitiesFields(enum.Enum):
    BLOCK_REFERENCES = 'BlockReferences'
    TEXT = 'Text'
    TYPE = 'Type'
    SCORE = 'Score'


class BlockReferenceFields(enum.Enum):
    BEGIN_OFFSET = 'BeginOffset'
    END_OFFSET = 'EndOffset'
    BLOCK_ID = 'BlockId'
    CHILD_BLOCKS = 'ChildBlocks'


class ChildBlockFields(enum.Enum):
    BEGIN_OFFSET = 'BeginOffset'
    END_OFFSET = 'EndOffset'
    CHILD_BLOCK_ID = 'ChildBlockId'


class ChildBlockSchema(Schema.from_dict({
    ChildBlockFields.BEGIN_OFFSET.value: fields.Int(required=True),
    ChildBlockFields.END_OFFSET.value: fields.Int(required=True),
    ChildBlockFields.CHILD_BLOCK_ID.value: fields.Str(required=True)
})):
    class Meta:
        unknown = EXCLUDE


class BlockReferenceSchema(Schema.from_dict({
    BlockReferenceFields.CHILD_BLOCKS.value: fields.List(
        fields.Nested(ChildBlockSchema), required=False, allow_none=True
    ),
    BlockReferenceFields.END_OFFSET.value: fields.Int(required=True),
    BlockReferenceFields.BEGIN_OFFSET.value: fields.Int(required=True),
    BlockReferenceFields.BLOCK_ID.value: fields.Str(required=True)
})):
    class Meta:
        unknown = EXCLUDE


class EntityAnnotationSchema(Schema.from_dict({
    EntitiesFields.BLOCK_REFERENCES.value: fields.List(
        fields.Nested(BlockReferenceSchema), required=False, allow_none=True
    ),
    EntitiesFields.TEXT.value: fields.Str(required=True),
    EntitiesFields.TYPE.value: fields.Str(required=True),
    EntitiesFields.SCORE.value: fields.Float(allow_none=True)
})):
    class Meta:
        unknown = EXCLUDE


# Blocks objects


class BlockFields(enum.Enum):
    # Block Object Fields
    BLOCK_TYPE = 'BlockType'
    ID = 'Id'
    TEXT = 'Text'
    GEOMETRY = 'Geometry'
    RELATIONSHIPS = 'Relationships'
    PAGE = 'Page'


class GeometryFields(enum.Enum):
    BOUNDING_BOX = 'BoundingBox'
    POLYGON = 'Polygon'


class BoundingBoxFields(enum.Enum):
    WIDTH = 'Width'
    TOP = 'Top'
    LEFT = 'Left'
    HEIGHT = 'Height'


class PolygonCoordinateFields(enum.Enum):
    X = 'X'
    Y = 'Y'


class RelationshipFields(enum.Enum):
    IDS = 'Ids'
    TYPE = 'Type'


class PolygonSchema(Schema.from_dict({
    PolygonCoordinateFields.X.value: fields.Float(required=True),
    PolygonCoordinateFields.Y.value: fields.Float(required=True)
})):
    class Meta:
        unknown = EXCLUDE


class BoundingBoxSchema(Schema.from_dict({
    BoundingBoxFields.WIDTH.value: fields.Float(required=True),
    BoundingBoxFields.TOP.value: fields.Float(required=True),
    BoundingBoxFields.HEIGHT.value: fields.Float(required=True),
    BoundingBoxFields.LEFT.value: fields.Float(required=True)
})):
    class Meta:
        unknown = EXCLUDE


class RelationshipSchema(Schema.from_dict({
    RelationshipFields.IDS.value: fields.List(fields.Str(), required=False),
    RelationshipFields.TYPE.value: fields.Str(required=False)
})):
    class Meta:
        unknown = EXCLUDE


class GeometrySchema(Schema.from_dict({
    GeometryFields.BOUNDING_BOX.value: fields.Nested(BoundingBoxSchema, required=True),
    GeometryFields.POLYGON.value: fields.List(
        fields.Nested(PolygonSchema), required=True
    )
})):
    class Meta:
        unknown = EXCLUDE


class BlockSchema(Schema.from_dict({
    BlockFields.GEOMETRY.value: fields.Nested(GeometrySchema, required=True),
    BlockFields.ID.value: fields.Str(required=True),
    BlockFields.TEXT.value: fields.Str(allow_none=True),
    BlockFields.PAGE.value: fields.Int(allow_none=True),
    BlockFields.RELATIONSHIPS.value: fields.List(
        fields.Nested(RelationshipSchema), default=[], allow_none=True
    ),
    BlockFields.BLOCK_TYPE.value: fields.Str(required=True)
})):
    class Meta:
        unknown = EXCLUDE

    @validates_schema
    def validate_text_field(self, data, **kwargs):
        if data[BlockFields.BLOCK_TYPE.value] in ["WORD", "LINE"]:
            if not data.get(BlockFields.TEXT.value):
                raise ValidationError("Text must be present for WORD and LINE blocks")


class AnnotationSchema(Schema.from_dict({
    Fields.VERSION.value: fields.Str(required=True),
    Fields.BLOCKS.value: fields.List(fields.Nested(BlockSchema), required=True),
    Fields.ENTITIES.value: fields.List(fields.Nested(EntityAnnotationSchema), required=True),
    Fields.DOCUMENT_METADATA.value: fields.Dict(required=True),
    Fields.DOCUMENT_TYPE.value: fields.Str(required=True)
})):
    class Meta:
        unknown = EXCLUDE
