# Generated by Django 4.0.3 on 2022-04-18 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminhome', '0006_alter_vehicle_insurance_expiry_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='bill_detail_id',
        ),
        migrations.AddField(
            model_name='billdetail',
            name='booking_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='bills', to='adminhome.booking'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='pc_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='booking', to='adminhome.parkingcategory'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='billdetail',
            name='payment_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bills', to='adminhome.payment'),
        ),
    ]
