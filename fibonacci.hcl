job "fibonacci" {

  datacenters = ["dc1"]

  group "python" {
    count = 1

    task "fibonacci" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver = "raw_exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.

      // artifact {
      //     source      = "git@github.com:UnholyDk/coursework.git"
      //     destination = "local/repo"
      //   options {
      //     sshkey = "${base64encode(file(pathexpand("~/.ssh/id_rsa")))}"
      //   }
      // }

      config {
        command = "python3"
        args = ["/Users/niyaz/forStudy/coursework/script.py"]
      }

      resources {
        cpu    = 500 # 500 MHz
        memory = 256 # 256MB
      }
    }
  }
}
