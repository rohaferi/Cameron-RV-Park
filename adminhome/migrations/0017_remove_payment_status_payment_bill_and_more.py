# Generated by Django 4.0.3 on 2022-04-25 07:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminhome', '0016_booking_lease_sign_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='status',
        ),
        migrations.AddField(
            model_name='payment',
            name='bill',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='adminhome.billdetail'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='state',
            field=models.CharField(choices=[('new', 'New Booking'), ('pending_approval', 'Pending Approval'), ('pending_lease', 'Pending Lease'), ('pending_slot', 'Pending Slot'), ('rejected', 'Rejected Booking'), ('approved', 'Approved Booking'), ('canceled_before_lease', 'Canceled Before Lease'), ('canceled', 'Canceled Booking'), ('paid', 'Paid Booking'), ('unpaid', 'Unpaid Booking')], default='new', max_length=30),
        ),
    ]