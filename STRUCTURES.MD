# Database Structures

## Groups

| Field Name  | Description                                | Data Type | Source           |
|-------------|--------------------------------------------|-----------|------------------|
| id          | An identifier for the group.               | Number    | System Generated |
| name        | The name of the group.                     | Text      | User Input       |
| description | A small description of the group’s purpose | Text      | User Input       |


## Messages

| Field Name  | Description                                | Data Type | Source           |
|-------------|--------------------------------------------|-----------|------------------|
| id          | An identifier for the message.             | Number    | System Generated |
| senderid    | The ID for the sender.                     | Number    | System Generated |
| channelid   | The iD for the recipient channel (a)       | Number    | System Generated |
| recipientid | The ID of the recipient user     (b)       | Number    | System Generated |
| datetime    | The date and time the message was sent.    | Text      | System Generated |
| content     | The raw content of the message.            | Text      | User Input       |


## Channels

| Field Name  | Description                                                                          | Data Type | Source           |
|-------------|--------------------------------------------------------------------------------------|-----------|------------------|
| id          | An identifier for the channel.                                                       | Number    | System Generated |
| groupid     | An identifier for the group it belongs to.                                           | Number    | System Generated |
| name        | The name of the channel.                                                             | Text      | User Input       |
| description | A description of the channel’s purpose.                                              | Text/None | User Input       |
| slowmode    | The time (in seconds) that users must wait between sending messages in that channel. | Number    | User Input       |


## Users

| Field Name    | Description                                                             | Data Type | Source                                             |
|---------------|-------------------------------------------------------------------------|-----------|----------------------------------------------------|
| id            | 969254887621820526                                                      | Number    | System Generated                                   |
| username      | tobezdev                                                                | Text      | User Input                                         |
| displayname   | tobezdev :)                                                             | Text      | User Input                                         |
| email         | toby@tobezdev.com                                                       | Text      | User Input                                         |
| password_hash | sha256:7cdbcff191889488068f6cff105b17b3c7d95f36924504375710d0e89122072a | Text      | User Input (and then hashed for security purposes) |
