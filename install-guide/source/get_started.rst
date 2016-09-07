==============================
Backup and DR service Overview
==============================

Freezer is a Backup Restore DR as a Service platform that helps you to automate
the data backup and restore process.

The service features a RESTful API, which can be used to maintain the status of
your jobs, backups and metadata.

This chapter assumes a working setup of OpenStack following the base
Installation Guide.


Concepts and definitions
========================

*hostname* is _probably_ going to be the host fqdn.

*backup_id*
defined as `container_hostname_backupname_timestamp_level` uniquely
identifies a backup

*backup_set*
defined as `container_hostname_backupname` identifies a group of related
backups which share the same container,hostname and backupname

