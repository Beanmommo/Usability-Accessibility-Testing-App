import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

import "./ResultBox.css";

const UploadBox = ({ resultFiles, updateResultFiles, currentAppStatus, updateCurrentAppStatus }) => {
  const [buttonState, setButtonState] = useState(false);
  const [buttonValue, setButtonValue] = useState("Upload File");
  const [selectedFile, setSelectedFile] = useState(null);

  //eslint-disable-next-line
  const [taskId, setTaskId] = useState(['rand']);

  //eslint-disable-next-line
  const canAccept = (file) => {
    return ['apk'];
  };

  useEffect(() => {
    console.log("The current stored result files are" + resultFiles);
    console.log("The current app status is " + currentAppStatus);
  }, [currentAppStatus, resultFiles]);

  const task_url = "http://localhost:5005/task";
  const apk_upload_url = "http://localhost:5005/upload";

  const getStatus = (taskID) => {
    fetch(`${task_url}/${taskID}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      },
    })
      .then(response => response.json())
      .then(res => {
        console.log(res);

        const taskStatus = res.task_status;

        if (taskStatus === 'SUCCESS') {
          setButtonState(false);
          setButtonValue("Upload again");
          updateCurrentAppStatus("RESULTS READY");
          return true;
        } else if (taskStatus === 'FAILURE') {
          setButtonState(false);
          setButtonValue("Upload again");
          updateCurrentAppStatus("TASK FAILED");
          return false;
        };

        setTimeout(function() {
          getStatus(res.task_id);
        }, 1000);
      }).catch(err => console.log(( err )));
  };

  const onDropAccepted = useCallback(acceptedFiles => {
    console.log("[1] upload start.");
    setButtonState(true);
    setSelectedFile(acceptedFiles[0]);

    acceptedFiles.forEach(file => {
      console.log(JSON.stringify(file));
    });

    var formData = new FormData();


    acceptedFiles.forEach(file => {
      // formData.append("file", file);
      formData.append("file", file);
      formData.append("filename", file.name);
      // formData.append("content", file);
      // console.log(typeof(file));
      // console.log(file);
      // console.log(formData);
      console.log(`Sending ${file.path} to server.`);
      fetch(apk_upload_url, {
        method: 'POST',
        body: formData,
        // body: { content: file, name: file.path },
      }).then(response => response.json()).then(data => {

        console.log("done");

        ///////////////////////////////////////////////////////////////
        //          Update and save the task_id for backend          //
        ///////////////////////////////////////////////////////////////
        setTaskId(prev => {
          return [...prev, data['task_id']];
        });

        console.log(data['task_id']);

        ///////////////////////////////////////////////////////////////
        //                       Restore button                      //
        ///////////////////////////////////////////////////////////////

        // setButtonState(false);
        const status = "getting results";
        setButtonValue(status);
        updateCurrentAppStatus(status);

        console.log("getting status");
        getStatus(data['task_id']);
      });
    });

  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDropAccepted: onDropAccepted,
    maxFiles: 1,
    disabled: buttonState,
    // validator: canAccept
  });

  return (
    <div className="result-box-root">
      <div{...getRootProps()} disabled={buttonState}>
        <input {...getInputProps()} disabled={buttonState} />

        <div className="result-box-full-width">
          <img className="result-box-icon" src={require("./content/apk-image.png")} alt={""} />
          <img className="result-box-icon" src={require("./content/apk-image.png")} alt={""} />
        </div>

        <div className="result-vspacing-10"> </div>

        <div className="result-box-full-width">
          <p className="result-box-text-30">{selectedFile ? selectedFile.name : 'Drop APK or MP4 here'}</p>
        </div>

        <div className="result-box-full-width">
          <div className="result-box-center-bar">
            {/* TODO actual progess bar */}
            <div className="result-box-line result-box-left" />
            <div className="result-box-line result-box-right" />

            <p className="result-box-text-20 result-text-center">or</p>
          </div>
        </div>

        <div className="result-box-full-width">
          {/* TODO functional button */}
          <button
            className={buttonState ? "result-box-view-button result-button-disabled" : "result-box-view-button result-button-enabled"}
            disabled={buttonState}>{buttonValue}
          </button>
        </div>
      </div>
    </div>
  );
}

export default UploadBox;
