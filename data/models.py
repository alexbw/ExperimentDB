from django.db import models
from django.template.defaultfilters import slugify

from external.models import Reference

class Protocol(models.Model):
    """Describes the protocol or protocols used to perform each experiment.  
    
    This model stores information about the protocol used for an experiment.    
    The only required field is the protocol.
    An experiment may have several protocols attached to it.  For example, one could culture and transfect cells, then generate lysates then do some western blots.
    
    Since migrating to a mediawiki based protocol storage system, the wiki_page attribute indicates the protocol wiki page.  In this model, the **protocol_revision** attribute indicates the particular revision of the protocol used for that particular experiment.  In this way a permalink can be generated to the specific protocol used for a particular experiment.  To find the protocol revision number, mouse over the permanent link on the protocol and record the number at the end of the url.
    """
       
    protocol = models.CharField(max_length=50)
    protocol_slug = models.SlugField(max_length=25, blank=True, null=True)
    reference = models.ManyToManyField(Reference, blank=True)
    protocol_file = models.FileField(upload_to='protocol', blank=True, null=True)
    protocol_revision = models.IntegerField(blank=True, null=True, help_text="ProtocolWiki page revision number")
    wiki_page = models.CharField(max_length=75, blank=True, null=True, help_text="ProtocolWiki page (via MediaWiki)")
    comments = models.TextField(max_length=500, blank=True, null=True)	
    public = models.BooleanField()
    published = models.BooleanField()
    inactive = models.BooleanField()

    def __unicode__(self):
        return u'%s ' % self.protocol

    @models.permalink
    def get_absolute_url(self):
        """The absolute url for a protocol is defined by the protocol-detail view."""
        return ('protocol-detail', [str(self.id)]) 
        
    def save(self, *args, **kwargs):
        '''The save command is over-ridden to automatically generate the protocol-slug for the first save.'''
        if not self.id:
            self.protocol_slug = slugify(self.protocol)
        super(Protocol, self).save(*args, **kwargs)            

	class Meta:
		ordering = ['-protocol']


class Experiment(models.Model):
    """Experiment objects are the central objects of this database.
    
    Experiment objects contain all details about an experiment including reagents, parameters, notes, results and data."""
    project = models.ManyToManyField('projects.Project', blank=True, null=True)
    subproject = models.ManyToManyField('projects.SubProject', blank=True, null=True)
    experimentID = models.SlugField(max_length=50, help_text="ie DB-2008-11-11-A", primary_key=True)
    experiment = models.CharField(max_length=100)
    protocol = models.ManyToManyField('Protocol', blank=True, null=True)
    assay = models.CharField(max_length=100, blank=True, null=True)
    experiment_date = models.DateField(help_text="Date Performed")
    cellline = models.ManyToManyField('reagents.Cell', blank=True, null=True)
    antibodies = models.ManyToManyField('reagents.Antibody', blank=True, null=True)
    chemicals = models.ManyToManyField('reagents.Chemical', blank=True, null=True)
    constructs = models.ManyToManyField('reagents.Construct', blank=True, null=True)
    siRNA = models.ManyToManyField('reagents.Primer', blank=True, null=True, limit_choices_to = {'primer_type': 'siRNA'})
    strain = models.ManyToManyField('reagents.Strain', blank=True, null=True)
    animal_model = models.ManyToManyField('reagents.AnimalStrain', blank=True, null=True)
    animal_cohort = models.ManyToManyField('AnimalCohort', blank=True, null=True)
    comments = models.TextField(max_length=500, blank=True, null=True)
    researcher = models.ManyToManyField('external.Contact', blank=True, null=True)
    protein = models.ManyToManyField('proteins.Protein', blank=True, null=True)
    public = models.BooleanField()
    published = models.BooleanField()
    sample_storage = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        """The unicode representation of an experiment object is the experiment on assay; date."""
        return u'%s on %s; %s' % (self.experiment, self.assay, self.experiment_date)

    @models.permalink
    def get_absolute_url(self):
        """The default url for an experiment is defined for the experiment-detail."""
        return ('experiment-detail', [str(self.experimentID)]) 

    class Meta:
        """The default ordering for experiments is in reverse of the experiment_date."""
        ordering = ['-experiment_date']

class Result(models.Model):
	experiment = models.ForeignKey('Experiment')
	conclusions = models.TextField(max_length=500, blank=True)
	#datafile = models.MultiFileField(upload_to='raw/%Y/%m/%d', blank=True)	
	file1 = models.FileField(upload_to='raw/%Y/%m/%d', blank=True)
	file2 = models.FileField(upload_to='raw/%Y/%m/%d', blank=True)
	file3 = models.FileField(upload_to='raw/%Y/%m/%d', blank=True)
	rawscan1 = models.ImageField(upload_to='raw/%Y/%m/%d', blank=True)
	rawscan2 = models.ImageField(upload_to='raw/%Y/%m/%d', blank=True)
	rawscan3 = models.ImageField(upload_to='raw/%Y/%m/%d', blank=True)
	rawscan4 = models.ImageField(upload_to='raw/%Y/%m/%d', blank=True)
	rawscan5 = models.ImageField(upload_to='raw/%Y/%m/%d', blank=True)
	result_figure1 = models.ImageField(upload_to='final/%Y/%m/%d', blank=True)
	result_figure2 = models.ImageField(upload_to='final/%Y/%m/%d', blank=True)
	public = models.BooleanField()
	published = models.BooleanField()
	def __unicode__(self):
		return u'%s ' % self.experiment
	def get_absolute_url(self):
		return "/result/%i/" % self.id


class Sequencing(models.Model):
	clone_name = models.CharField(max_length=15)
	construct = models.ForeignKey('reagents.Construct')
	primer = models.ForeignKey('reagents.Primer')
	file = models.FileField(upload_to='sequencing/%Y/%m/%d', blank=True, null=True)
	sequence = models.CharField(max_length=1500)
	correct = models.BooleanField()
	notes = models.TextField(max_length=250,blank=True)
	date = models.DateField(blank=True, null=True)
	sample_number = models.IntegerField(max_length=8, blank=True, null=True)
	gel_number = models.IntegerField(max_length=8, blank=True, null=True)
	lane_number = models.IntegerField(max_length=3, blank=True, null=True)
	def __unicode__(self):
		return u'%s-%s' % (self.construct,self.clone_name)
        
class AnimalCohort(models.Model):

    """This model describes a particular cohort of animals.  
    
    As an example, an experiment might be dont with a particular knockout model, over several cohorts.
    This model defines two required classes, name and a many to many field for  :class:`~experimentdb.reagents.models.AnimalStrain`, and optional notes, start and end dates.
    The unicode name of this is "name" field and the url is /cohort/id where id is the primary key."""
    name = models.CharField(max_length=50)
    animal_model = models.ManyToManyField('reagents.AnimalStrain')
    date_start = models.DateField(blank=True, null=True, help_text="Cohort Start Date")
    date_end = models.DateField(blank=True, null=True, help_text="Cohort End Date")
    notes = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return u'%s' % (self.name) 
    def get_absolute_url(self):
        return "/cohort/%i/" % self.id        
