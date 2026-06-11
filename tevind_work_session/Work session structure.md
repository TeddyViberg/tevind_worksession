Work session is An app with the sole focus of creating a vue page for managing a work session. 

## What is a work session?
A work session is when a human is spending time to do a task. The human starts the session -> works -> and then finnishes the session. 


## Dependencies.
### tevind_project
This is were tasks and task enties are located. These tasks are worked on. A work session needs to know what can be worked on (tasks) and make a task entry when work has been done on that task.

### tevind_workforce
The human making the work is contracted. These contracts are located in tevind_workforce. When a work session is finnished a work entry on that contract is made. 


## File structure
This App follows standard tevind vue page application. The api pythonfile only have endpoints, the main functions are in services.

```text
{{generated_app}}/
└─{{generated_app}}/
  ├─{{desk_page_module}}/
  │ └─page/
  │   └─{{page_name}}/
  │     ├─{{page_name}}.json
  │     └─{{page_name}}.js
  ├─public/
  │ └─js/
  │   └─desk_pages/
  │     └─{{page_name}}/
  │       ├─{{RootComponent}}.vue
  │       ├─{{page_name}}.bundle.js
  │       ├─api.js
  │       ├─schema.js
  │       └─components/
  ├─api/
  │ └─{{page_name}}.py
  └─services/
    └─{{page_name}}_service.py
```