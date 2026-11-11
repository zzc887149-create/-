using UnityEngine;

namespace ZhaoLeiBirdsNestV3 {
public class BirdsNestFlyCamera : MonoBehaviour {
    public Transform[] viewpoints;
    public Transform[] targets;
    public float speed = 25f;
    public int activeView;
    public void Jump(int index) {
        if (viewpoints == null || index < 0 || index >= viewpoints.Length) return;
        activeView=index; transform.position=viewpoints[index].position;
        transform.rotation=Quaternion.LookRotation(targets[index].position-transform.position,Vector3.up);
    }
    void Update() {
        float x=0,y=0,z=0; bool fast=false,look=false; Vector2 delta=Vector2.zero;
#if ENABLE_INPUT_SYSTEM
        var k=UnityEngine.InputSystem.Keyboard.current;
        var m=UnityEngine.InputSystem.Mouse.current;
        if(k!=null) {
            x=(k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0);
            z=(k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0);
            y=(k.eKey.isPressed?1:0)-(k.qKey.isPressed?1:0);
            fast=k.leftShiftKey.isPressed||k.rightShiftKey.isPressed;
            var keys=new[]{k.digit1Key,k.digit2Key,k.digit3Key,k.digit4Key,k.digit5Key,k.digit6Key,k.digit7Key,k.digit8Key,k.digit9Key};
            for(int i=0;i<keys.Length;i++) if(keys[i].wasPressedThisFrame)Jump(i);
        }
        if(m!=null){look=m.rightButton.isPressed;delta=m.delta.ReadValue()*.16f;}
#elif ENABLE_LEGACY_INPUT_MANAGER
        x=(Input.GetKey(KeyCode.D)?1:0)-(Input.GetKey(KeyCode.A)?1:0);
        z=(Input.GetKey(KeyCode.W)?1:0)-(Input.GetKey(KeyCode.S)?1:0);
        y=(Input.GetKey(KeyCode.E)?1:0)-(Input.GetKey(KeyCode.Q)?1:0);
        fast=Input.GetKey(KeyCode.LeftShift)||Input.GetKey(KeyCode.RightShift);
        look=Input.GetMouseButton(1);delta=new Vector2(Input.GetAxisRaw("Mouse X"),Input.GetAxisRaw("Mouse Y"))*2;
        for(int i=0;i<9;i++)if(Input.GetKeyDown((KeyCode)((int)KeyCode.Alpha1+i)))Jump(i);
#endif
        transform.position+=(transform.right*x+transform.forward*z+Vector3.up*y)*speed*(fast?4:1)*Time.unscaledDeltaTime;
        if(look){var a=transform.eulerAngles;float pitch=a.x>180?a.x-360:a.x;transform.rotation=Quaternion.Euler(Mathf.Clamp(pitch-delta.y,-89,89),a.y+delta.x,0);}
    }
}
}

