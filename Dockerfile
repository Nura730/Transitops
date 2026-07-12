FROM odoo:17.0

# Copy the custom addons into the Odoo addons directory
COPY ./transit_ops /mnt/extra-addons/transit_ops

# Switch back to the non-root odoo user
USER odoo
