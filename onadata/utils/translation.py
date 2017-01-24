from modeltranslation.translator import TranslationOptions

class NameTranslationOptions(TranslationOptions):
	fields = ('name',)

class NameDescriptionTranslationOptions(TranslationOptions):
	fields = ('name', )