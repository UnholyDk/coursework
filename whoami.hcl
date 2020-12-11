job "whoami" {

  datacenters = ["dc1"]
  
  type = "batch"

  group "blabla" {
    count = 1

    task "check_user" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver = "exec"
      user = "niyaz"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.

      artifact {
        source      = "git::https://github.com/UnholyDk/data.git"
        destination = "local/repo"
      }

      config {
        command = "/usr/bin/whoami"
      }
    }
  }
}
