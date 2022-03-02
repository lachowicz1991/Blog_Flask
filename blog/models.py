from blog import database
import re
from peewee import *
from playhouse.sqlite_ext import *
class Entry(Model):
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())
        ret = super(Entry,self).save(*args, **kwargs)

        # Stores search content
        self.update_search_index()
        return ret

    def update_search_index(self):
        search_content = '\n'.join(self.title, self.content)
        try:
            fts_entry = FTSEntry.get(FTSEntry.docid == self.id)
        except FTSEntry.DoesNotExist:
            FTSEntry.create(docid=self.id, content=search_content)
        else:
            fts_entry.content = search_content
            fts_entry.save()


class FTSEntry(FTSModel):
    content = SearchField()

    class Meta:
        database = database