



class CalendarEvent(BaseModelMixin):
    name = models.CharField(max_length=200, verbose_name="Nom de l'événement")
    date = models.DateField(verbose_name="Date de l'événement")
    event_type = models.CharField(
        max_length=50, 
        choices=CalendarEventType.choices, 
        default=CalendarEventType.OTHER, 
        verbose_name="Type d'événement"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description de l'événement")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Date et heure de début")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date et heure de fin")
    comments = models.CharField(max_length=500, blank=True, null=True, verbose_name="Commentaires")
    code = models.CharField(max_length=100, unique=True, verbose_name="Code de l'événement")
    recurrent = models.BooleanField(default=False, verbose_name="Récurrent")
    status = models.CharField(max_length=100, verbose_name="Statut de l'événement")

    class Meta:
        verbose_name = "Événement du calendrier"
        verbose_name_plural = "Événements du calendrier"
        unique_together = ('name', 'date', 'event_type')

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()} - {self.date})"
    

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class CalendarEventSettings(SingletonMixin):
    show_anniversary = models.BooleanField(default=False, verbose_name="Anniversaires")
    show_deadline = models.BooleanField(default=False, verbose_name="Démarrages")
    show_meeting = models.BooleanField(default=False, verbose_name="Meetings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING,
        null=True, 
        related_name="calender_event_settings",
        verbose_name="Mis à jour par"
    )


    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
