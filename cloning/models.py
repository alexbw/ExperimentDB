'''This package sets the data storage parameters for the models app.

It is dependent on the data package models for Sequencing and Protocol.
There is also a dependency to the reagents package for Construct and Primer objects and from the external package a Contact.
'''

from django.db import models

CLONING_TYPE = (
	('PCR', 'PCR Based'),
	('digest', 'Digestion and Ligation'),
	('LIC', 'Ligation Independent Cloning'),
)

class Cloning(models.Model):
    """This model stores details about the generation of new recombinant DNA molecules.
    
    The required fields for this object are the Construct and the cloning_type.
    """

    date_completed = models.DateField(blank=True, null=True)
    construct = models.ForeignKey('reagents.Construct', help_text="Result of Cloning Project", related_name="final_clone")
    cloning_type = models.CharField(max_length=25, choices=CLONING_TYPE)
    vector = models.ForeignKey('reagents.Construct', blank=True, null=True, related_name="recipient_vector")
    vector_CIP = models.BooleanField()
    insert = models.CharField(max_length=100, blank=True, null=True)
    primer_5prime = models.ForeignKey('reagents.Primer', blank=True, null=True, related_name='5_Primer', verbose_name="5' PCR Primer")
    primer_3prime = models.ForeignKey('reagents.Primer', blank=True, null=True, related_name='3_Primer', verbose_name="3' PCR Primer")
    restriction_enzyme_5prime = models.CharField(max_length=7, blank=True, null=True, verbose_name="insert 5' site")
    restriction_enzyme_3prime = models.CharField(max_length=7, blank=True, null=True, verbose_name="vector 3' site")    
    vector_restriction_enzyme_5prime = models.CharField(max_length=7, blank=True, null=True, verbose_name="vector 5' site")
    vector_restriction_enzyme_3prime = models.CharField(max_length=7, blank=True, null=True, verbose_name="vector 3' site")    
    destroyed_5prime = models.BooleanField(verbose_name="is the 5' site destroyed?")
    destroyed_3prime = models.BooleanField(verbose_name="is the 3' site destroyed?")    
    ligation_temperature = models.IntegerField(blank=True, null=True, help_text = "in degrees Celsius")
    ligation_time = models.TimeField(blank=True, null=True, help_text = "HH:MM")
    gel = models.ImageField(upload_to = 'cloning/%Y/%m/%d', blank=True, null=True)
    sequencing = models.ManyToManyField('data.Sequencing', blank=True, null=True)
    researcher = models.ManyToManyField('external.Contact', blank=True, null=True)
    notes = models.TextField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        '''The unicode representation for a Cloning object is the construct name (from the Construct object) followed by the word cloning.'''
        return u'%s cloning' % self.construct

    @models.permalink
    def get_absolute_url(self):
        '''The permalink for a cloning object is the primary key linked to **/clones/cloning/<ID>**'''
        return ('cloning_detail', [str(self.id)])

class Mutagenesis(models.Model):
    """This model contains data describing the generation of muationns in clones"""
    construct = models.ForeignKey('reagents.Construct', related_name="mutant")
    mutation = models.CharField(max_length=25)
    template = models.ForeignKey('reagents.Construct', related_name="template")
    date_completed = models.DateField()
    method = models.CharField(max_length=50, default = "Stratagene QuickChange")
    protocol = models.ForeignKey('data.Protocol', blank=True, null=True)
    sense_primer = models.ForeignKey('reagents.Primer', blank=True, null=True, related_name="sense_primer")
    antisense_primer = models.ForeignKey('reagents.Primer', blank=True, null=True, related_name="antisense_primer")
    colonies = models.IntegerField(blank=True, null=True)
    sequencing = models.ManyToManyField('data.Sequencing', blank=True, null=True)
    researcher = models.ManyToManyField('external.Contact', blank=True, null=True)
    notes = models.TextField(max_length=250, blank=True)
    class Meta:
        verbose_name_plural = "Mutageneses"
    def __unicode__(self):
        return u'%s ' % self.construct
    def get_absolute_url(self):
        return "experimentdb/clones/mutagenesis/%i/" % self.id
